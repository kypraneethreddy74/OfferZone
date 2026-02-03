"""
Admin Dashboard API Routes
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text, func
from datetime import datetime, timedelta, timezone

from db import get_db
from models import User, Wishlist, PriceAlert, AlertNotification, UserRole
from auth.dependencies import require_admin

router = APIRouter(prefix="/admin", tags=["Admin Dashboard"])


# ============================================
# DASHBOARD OVERVIEW
# ============================================

@router.get("/dashboard")
async def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Get comprehensive admin dashboard stats"""
    
    today = datetime.now(timezone.utc).date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    
    # User Stats
    total_users = db.query(User).count()
    verified_users = db.query(User).filter(User.is_verified == True).count()
    active_users = db.query(User).filter(User.is_active == True).count()
    admin_users = db.query(User).filter(User.role == UserRole.ADMIN).count()
    
    users_today = db.query(User).filter(
        func.date(User.created_at) == today
    ).count()
    
    users_this_week = db.query(User).filter(
        func.date(User.created_at) >= week_ago
    ).count()
    
    # Wishlist Stats
    total_wishlists = db.query(Wishlist).count()
    users_with_wishlists = db.query(Wishlist.user_id).distinct().count()
    
    # Alert Stats
    total_alerts = db.query(PriceAlert).count()
    active_alerts = db.query(PriceAlert).filter(PriceAlert.is_active == True).count()
    triggered_alerts = db.query(PriceAlert).filter(PriceAlert.is_triggered == True).count()
    
    alerts_triggered_today = db.query(AlertNotification).filter(
        func.date(AlertNotification.created_at) == today
    ).count()
    
    emails_sent_today = db.query(AlertNotification).filter(
        func.date(AlertNotification.email_sent_at) == today,
        AlertNotification.email_sent == True
    ).count()
    
    # Product Stats (from existing tables)
    product_stats = db.execute(text("""
        SELECT 
            COUNT(DISTINCT model_id) as total_products,
            COUNT(DISTINCT brand) as total_brands,
            COUNT(DISTINCT platform) as total_platforms,
            ROUND(AVG(sale_price), 2) as avg_price
        FROM tv_platform_latest_master
        WHERE sale_price > 0
    """)).fetchone()
    
    return {
        "user_metrics": {
            "total_users": total_users,
            "verified_users": verified_users,
            "unverified_users": total_users - verified_users,
            "active_users": active_users,
            "admin_users": admin_users,
            "users_today": users_today,
            "users_this_week": users_this_week,
            "verification_rate": round(verified_users / total_users * 100, 1) if total_users > 0 else 0
        },
        "wishlist_metrics": {
            "total_items": total_wishlists,
            "users_with_wishlists": users_with_wishlists,
            "avg_items_per_user": round(total_wishlists / users_with_wishlists, 1) if users_with_wishlists > 0 else 0
        },
        "alert_metrics": {
            "total_alerts": total_alerts,
            "active_alerts": active_alerts,
            "inactive_alerts": total_alerts - active_alerts,
            "triggered_alerts": triggered_alerts,
            "alerts_triggered_today": alerts_triggered_today,
            "emails_sent_today": emails_sent_today
        },
        "product_metrics": {
            "total_products": product_stats.total_products if product_stats else 0,
            "total_brands": product_stats.total_brands if product_stats else 0,
            "total_platforms": product_stats.total_platforms if product_stats else 0,
            "avg_price": float(product_stats.avg_price) if product_stats and product_stats.avg_price else 0
        },
        "generated_at": datetime.now(timezone.utc).isoformat()
    }


# ============================================
# USER MANAGEMENT
# ============================================

@router.get("/users")
async def get_users(
    page: int = 1,
    page_size: int = 20,
    search: str = None,
    role: str = None,
    verified: bool = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Get paginated list of users"""
    
    query = db.query(User)
    
    if search:
        query = query.filter(
            (User.name.ilike(f"%{search}%")) |
            (User.email.ilike(f"%{search}%"))
        )
    
    if role:
        query = query.filter(User.role == role)
    
    if verified is not None:
        query = query.filter(User.is_verified == verified)
    
    total = query.count()
    
    users = query.order_by(User.created_at.desc()).offset(
        (page - 1) * page_size
    ).limit(page_size).all()
    
    return {
        "users": [
            {
                "id": u.id,
                "name": u.name,
                "email": u.email,
                "role": u.role.value,
                "is_active": u.is_active,
                "is_verified": u.is_verified,
                "created_at": u.created_at.isoformat() if u.created_at else None,
                "wishlist_count": db.query(Wishlist).filter(Wishlist.user_id == u.id).count(),
                "alert_count": db.query(PriceAlert).filter(PriceAlert.user_id == u.id).count()
            }
            for u in users
        ],
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size
    }


@router.patch("/users/{user_id}")
async def update_user(
    user_id: int,
    is_active: bool = None,
    is_verified: bool = None,
    role: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Update user status"""
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Prevent self-demotion
    if user.id == current_user.id and role and role != "admin":
        raise HTTPException(status_code=400, detail="Cannot demote yourself")
    
    if is_active is not None:
        user.is_active = is_active
    
    if is_verified is not None:
        user.is_verified = is_verified
        if is_verified:
            user.verified_at = datetime.now(timezone.utc)
    
    if role:
        user.role = UserRole(role)
    
    db.commit()
    
    return {"success": True, "message": "User updated"}


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Delete a user"""
    
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot delete yourself")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db.delete(user)
    db.commit()
    
    return {"success": True, "message": "User deleted"}


# ============================================
# MOST WISHLISTED PRODUCTS
# ============================================

@router.get("/analytics/most-wishlisted")
async def get_most_wishlisted(
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Get most wishlisted products"""
    
    result = db.execute(text("""
        SELECT 
            w.model_id,
            COUNT(*) as wishlist_count,
            MIN(p.full_name) as product_name,
            MIN(p.brand) as brand,
            MIN(p.sale_price) as min_price,
            MIN(p.image_url) as image_url
        FROM wishlists w
        LEFT JOIN tv_platform_latest_master p ON w.model_id = p.model_id
        GROUP BY w.model_id
        ORDER BY wishlist_count DESC
        LIMIT :limit
    """), {"limit": limit})
    
    return [
        {
            "model_id": row.model_id,
            "wishlist_count": row.wishlist_count,
            "product_name": row.product_name,
            "brand": row.brand,
            "min_price": float(row.min_price) if row.min_price else None,
            "image_url": row.image_url
        }
        for row in result
    ]


# ============================================
# MOST ALERTED PRODUCTS
# ============================================

@router.get("/analytics/most-alerted")
async def get_most_alerted(
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Get products with most price alerts"""
    
    result = db.execute(text("""
        SELECT 
            a.model_id,
            COUNT(*) as alert_count,
            SUM(CASE WHEN a.is_active = 1 THEN 1 ELSE 0 END) as active_alerts,
            SUM(CASE WHEN a.is_triggered = 1 THEN 1 ELSE 0 END) as triggered_alerts,
            AVG(a.target_price) as avg_target_price,
            MIN(p.full_name) as product_name,
            MIN(p.brand) as brand,
            MIN(p.sale_price) as current_price
        FROM price_alerts a
        LEFT JOIN tv_platform_latest_master p ON a.model_id = p.model_id
        GROUP BY a.model_id
        ORDER BY alert_count DESC
        LIMIT :limit
    """), {"limit": limit})
    
    return [
        {
            "model_id": row.model_id,
            "alert_count": row.alert_count,
            "active_alerts": row.active_alerts,
            "triggered_alerts": row.triggered_alerts,
            "avg_target_price": float(row.avg_target_price) if row.avg_target_price else None,
            "product_name": row.product_name,
            "brand": row.brand,
            "current_price": float(row.current_price) if row.current_price else None
        }
        for row in result
    ]


# ============================================
# RECENT ALERT NOTIFICATIONS
# ============================================

@router.get("/analytics/recent-notifications")
async def get_recent_notifications(
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Get recent alert notifications"""
    
    result = db.execute(text("""
        SELECT 
            n.id,
            n.model_id,
            n.target_price,
            n.triggered_price,
            n.platform,
            n.email_sent,
            n.created_at,
            u.name as user_name,
            u.email as user_email,
            MIN(p.full_name) as product_name
        FROM alert_notifications n
        JOIN users u ON n.user_id = u.id
        LEFT JOIN tv_platform_latest_master p ON n.model_id = p.model_id
        GROUP BY n.id, n.model_id, n.target_price, n.triggered_price, 
                 n.platform, n.email_sent, n.created_at, u.name, u.email
        ORDER BY n.created_at DESC
        LIMIT :limit
    """), {"limit": limit})
    
    return [
        {
            "id": row.id,
            "model_id": row.model_id,
            "product_name": row.product_name,
            "target_price": float(row.target_price),
            "triggered_price": float(row.triggered_price),
            "platform": row.platform,
            "email_sent": row.email_sent,
            "user_name": row.user_name,
            "user_email": row.user_email,
            "created_at": row.created_at.isoformat() if row.created_at else None
        }
        for row in result
    ]


# ============================================
# USER GROWTH CHART DATA
# ============================================

@router.get("/analytics/user-growth")
async def get_user_growth(
    days: int = 30,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Get user registration data for chart"""
    
    result = db.execute(text("""
        SELECT 
            DATE(created_at) as date,
            COUNT(*) as new_users,
            SUM(CASE WHEN is_verified = 1 THEN 1 ELSE 0 END) as verified_users
        FROM users
        WHERE created_at >= DATE_SUB(CURDATE(), INTERVAL :days DAY)
        GROUP BY DATE(created_at)
        ORDER BY date
    """), {"days": days})
    
    return [
        {
            "date": str(row.date),
            "new_users": row.new_users,
            "verified_users": row.verified_users
        }
        for row in result
    ]


# ============================================
# ALERTS ACTIVITY CHART DATA
# ============================================

@router.get("/analytics/alerts-activity")
async def get_alerts_activity(
    days: int = 30,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Get alerts activity data for chart"""
    
    result = db.execute(text("""
        SELECT 
            DATE(created_at) as date,
            COUNT(*) as notifications_sent,
            SUM(CASE WHEN email_sent = 1 THEN 1 ELSE 0 END) as emails_sent
        FROM alert_notifications
        WHERE created_at >= DATE_SUB(CURDATE(), INTERVAL :days DAY)
        GROUP BY DATE(created_at)
        ORDER BY date
    """), {"days": days})
    
    return [
        {
            "date": str(row.date),
            "notifications_sent": row.notifications_sent,
            "emails_sent": row.emails_sent
        }
        for row in result
    ]


# ============================================
# RUN ALERT ENGINE MANUALLY
# ============================================

@router.post("/run-alert-engine")
async def run_alert_engine_manual(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Manually trigger alert engine run"""
    
    from alert_engine import AlertEngine
    
    try:
        engine = AlertEngine()
        engine.run()
        
        return {
            "success": True,
            "message": "Alert engine completed",
            "results": {
                "alerts_checked": engine.alerts_checked,
                "alerts_triggered": engine.alerts_triggered,
                "emails_sent": engine.emails_sent
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))