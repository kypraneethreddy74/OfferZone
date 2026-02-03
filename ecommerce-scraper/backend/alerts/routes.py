"""
Price Alert API Routes
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text, and_
from datetime import datetime, timezone
from typing import List

from db import get_db
from models import PriceAlert, AlertNotification, User
from auth.dependencies import get_current_verified_user, get_current_active_user
from .schemas import (
    AlertCreate, AlertUpdate, AlertResponse,
    AlertListResponse, AlertStatusResponse, AlertNotificationResponse
)

router = APIRouter(prefix="/alerts", tags=["Price Alerts"])


def get_product_details(db: Session, model_id: str) -> dict:
    """Get product details for an alert"""
    result = db.execute(text("""
        SELECT 
            MIN(full_name) as product_name,
            MIN(brand) as brand,
            MIN(image_url) as image_url,
            MIN(sale_price) as min_price,
            (SELECT platform FROM tv_platform_latest_master 
             WHERE model_id = :model_id AND sale_price > 0 
             ORDER BY sale_price ASC LIMIT 1) as best_platform
        FROM tv_platform_latest_master
        WHERE model_id = :model_id AND sale_price > 0
    """), {"model_id": model_id}).fetchone()
    
    if result:
        return {
            "product_name": result.product_name,
            "brand": result.brand,
            "image_url": result.image_url,
            "min_price": float(result.min_price) if result.min_price else None,
            "best_platform": result.best_platform
        }
    return {}


# ============================================
# GET ALL ALERTS
# ============================================

@router.get("", response_model=AlertListResponse)
async def get_alerts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all price alerts for current user"""
    
    alerts = db.query(PriceAlert).filter(
        PriceAlert.user_id == current_user.id
    ).order_by(PriceAlert.created_at.desc()).all()
    
    alert_responses = []
    active_count = 0
    triggered_count = 0
    
    for alert in alerts:
        product_details = get_product_details(db, alert.model_id)
        
        alert_responses.append(AlertResponse(
            id=alert.id,
            model_id=alert.model_id,
            target_price=alert.target_price,
            current_price=alert.current_price,
            is_active=alert.is_active,
            is_triggered=alert.is_triggered,
            trigger_count=alert.trigger_count,
            created_at=alert.created_at,
            last_notified_at=alert.last_notified_at,
            **product_details
        ))
        
        if alert.is_active:
            active_count += 1
        if alert.is_triggered:
            triggered_count += 1
    
    return AlertListResponse(
        alerts=alert_responses,
        total=len(alerts),
        active_count=active_count,
        triggered_count=triggered_count
    )


# ============================================
# CREATE ALERT
# ============================================

@router.post("", status_code=status.HTTP_201_CREATED)
async def create_alert(
    alert_data: AlertCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_verified_user)
):
    """Create a new price alert (requires verified email)"""
    
    # Check if alert already exists
    existing = db.query(PriceAlert).filter(
        and_(
            PriceAlert.user_id == current_user.id,
            PriceAlert.model_id == alert_data.model_id
        )
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Alert already exists for this product. Update the existing alert instead."
        )
    
    # Get current price
    price_result = db.execute(text("""
        SELECT MIN(sale_price) as min_price
        FROM tv_platform_latest_master
        WHERE model_id = :model_id AND sale_price > 0
    """), {"model_id": alert_data.model_id}).fetchone()
    
    if not price_result or not price_result.min_price:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    current_price = float(price_result.min_price)
    
    # Warn if target is higher than current
    if alert_data.target_price >= current_price:
        # Still create but mark as triggered
        is_triggered = True
    else:
        is_triggered = False
    
    # Create alert
    alert = PriceAlert(
        user_id=current_user.id,
        model_id=alert_data.model_id,
        target_price=alert_data.target_price,
        current_price=current_price,
        is_active=True,
        is_triggered=is_triggered,
        last_checked_at=datetime.now(timezone.utc)
    )
    
    db.add(alert)
    db.commit()
    db.refresh(alert)
    
    return {
        "success": True,
        "message": "Price alert created" + (" (already at target!)" if is_triggered else ""),
        "alert_id": alert.id,
        "current_price": current_price,
        "target_price": alert_data.target_price,
        "is_triggered": is_triggered
    }


# ============================================
# UPDATE ALERT
# ============================================

@router.patch("/{alert_id}")
async def update_alert(
    alert_id: int,
    update_data: AlertUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update a price alert"""
    
    alert = db.query(PriceAlert).filter(
        and_(
            PriceAlert.id == alert_id,
            PriceAlert.user_id == current_user.id
        )
    ).first()
    
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found"
        )
    
    if update_data.target_price is not None:
        alert.target_price = update_data.target_price
        # Reset triggered status when target changes
        if alert.current_price and update_data.target_price < alert.current_price:
            alert.is_triggered = False
    
    if update_data.is_active is not None:
        alert.is_active = update_data.is_active
    
    db.commit()
    
    return {
        "success": True,
        "message": "Alert updated",
        "alert_id": alert.id
    }


# ============================================
# DELETE ALERT
# ============================================

@router.delete("/{alert_id}")
async def delete_alert(
    alert_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete a price alert"""
    
    alert = db.query(PriceAlert).filter(
        and_(
            PriceAlert.id == alert_id,
            PriceAlert.user_id == current_user.id
        )
    ).first()
    
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found"
        )
    
    db.delete(alert)
    db.commit()
    
    return {
        "success": True,
        "message": "Alert deleted"
    }


# ============================================
# CHECK ALERT STATUS
# ============================================

@router.get("/check/{model_id}", response_model=AlertStatusResponse)
async def check_alert_status(
    model_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Check if user has alert for this product"""
    
    alert = db.query(PriceAlert).filter(
        and_(
            PriceAlert.user_id == current_user.id,
            PriceAlert.model_id == model_id
        )
    ).first()
    
    if alert:
        return AlertStatusResponse(
            has_alert=True,
            alert_id=alert.id,
            target_price=alert.target_price,
            is_active=alert.is_active
        )
    
    return AlertStatusResponse(has_alert=False)


# ============================================
# TOGGLE ALERT
# ============================================

@router.post("/toggle/{alert_id}")
async def toggle_alert(
    alert_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Toggle alert active status"""
    
    alert = db.query(PriceAlert).filter(
        and_(
            PriceAlert.id == alert_id,
            PriceAlert.user_id == current_user.id
        )
    ).first()
    
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found"
        )
    
    alert.is_active = not alert.is_active
    db.commit()
    
    return {
        "success": True,
        "is_active": alert.is_active,
        "message": f"Alert {'enabled' if alert.is_active else 'disabled'}"
    }


# ============================================
# GET NOTIFICATION HISTORY
# ============================================

@router.get("/notifications", response_model=List[AlertNotificationResponse])
async def get_notifications(
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get alert notification history"""
    
    query = text("""
        SELECT 
            n.id,
            n.model_id,
            n.target_price,
            n.triggered_price,
            n.platform,
            n.created_at,
            MIN(p.full_name) as product_name
        FROM alert_notifications n
        LEFT JOIN tv_platform_latest_master p ON n.model_id = p.model_id
        WHERE n.user_id = :user_id
        GROUP BY n.id, n.model_id, n.target_price, n.triggered_price, n.platform, n.created_at
        ORDER BY n.created_at DESC
        LIMIT :limit
    """)
    
    result = db.execute(query, {"user_id": current_user.id, "limit": limit})
    
    notifications = []
    for row in result:
        notifications.append(AlertNotificationResponse(
            id=row.id,
            model_id=row.model_id,
            target_price=row.target_price,
            triggered_price=row.triggered_price,
            platform=row.platform,
            created_at=row.created_at,
            product_name=row.product_name
        ))
    
    return notifications


# ============================================
# GET ALERT COUNT
# ============================================

@router.get("/count")
async def get_alert_count(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get alert counts"""
    
    total = db.query(PriceAlert).filter(
        PriceAlert.user_id == current_user.id
    ).count()
    
    active = db.query(PriceAlert).filter(
        and_(
            PriceAlert.user_id == current_user.id,
            PriceAlert.is_active == True
        )
    ).count()
    
    triggered = db.query(PriceAlert).filter(
        and_(
            PriceAlert.user_id == current_user.id,
            PriceAlert.is_triggered == True
        )
    ).count()
    
    return {
        "total": total,
        "active": active,
        "triggered": triggered
    }