"""
User Settings & Account Management Routes
"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime, timezone

from db import get_db
from models import User, Wishlist, PriceAlert, RefreshSession, EmailVerificationToken
from auth.dependencies import get_current_active_user
from auth.security import SecurityUtils
from email_service import EmailService

router = APIRouter(prefix="/settings", tags=["User Settings"])


# ============================================
# GET USER PROFILE
# ============================================

@router.get("/profile")
async def get_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get user profile with stats"""
    
    wishlist_count = db.query(Wishlist).filter(Wishlist.user_id == current_user.id).count()
    alert_count = db.query(PriceAlert).filter(PriceAlert.user_id == current_user.id).count()
    active_alerts = db.query(PriceAlert).filter(
        and_(PriceAlert.user_id == current_user.id, PriceAlert.is_active == True)
    ).count()
    
    return {
        "id": current_user.id,
        "name": current_user.name,
        "email": current_user.email,
        "role": current_user.role.value,
        "is_verified": current_user.is_verified,
        "verified_at": current_user.verified_at.isoformat() if current_user.verified_at else None,
        "created_at": current_user.created_at.isoformat() if current_user.created_at else None,
        "stats": {
            "wishlist_items": wishlist_count,
            "total_alerts": alert_count,
            "active_alerts": active_alerts
        }
    }


# ============================================
# UPDATE PROFILE
# ============================================

@router.patch("/profile")
async def update_profile(
    name: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update user profile"""
    
    if name:
        if len(name.strip()) < 2:
            raise HTTPException(status_code=400, detail="Name must be at least 2 characters")
        current_user.name = name.strip()
    
    db.commit()
    
    return {"success": True, "message": "Profile updated"}


# ============================================
# CHANGE PASSWORD
# ============================================

@router.post("/change-password")
async def change_password(
    current_password: str,
    new_password: str,
    confirm_password: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Change user password"""
    
    # Verify current password
    if not SecurityUtils.verify_password(current_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Current password is incorrect")
    
    # Validate new password
    if len(new_password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters")
    
    if new_password != confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")
    
    # Update password
    current_user.hashed_password = SecurityUtils.hash_password(new_password)
    
    # Revoke all other sessions
    db.query(RefreshSession).filter(
        RefreshSession.user_id == current_user.id
    ).update({"is_revoked": True})
    
    db.commit()
    
    # Send notification email
    background_tasks.add_task(
        EmailService.send_password_changed_email,
        current_user.email,
        current_user.name
    )
    
    return {"success": True, "message": "Password changed successfully"}


# ============================================
# ALERT PREFERENCES
# ============================================

@router.get("/alert-preferences")
async def get_alert_preferences(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get user's alert preferences"""
    
    total_alerts = db.query(PriceAlert).filter(
        PriceAlert.user_id == current_user.id
    ).count()
    
    active_alerts = db.query(PriceAlert).filter(
        and_(PriceAlert.user_id == current_user.id, PriceAlert.is_active == True)
    ).count()
    
    return {
        "email_notifications": True,  # Can be stored in user preferences table
        "total_alerts": total_alerts,
        "active_alerts": active_alerts,
        "alerts_enabled": active_alerts > 0
    }


# ============================================
# DISABLE ALL ALERTS
# ============================================

@router.post("/disable-all-alerts")
async def disable_all_alerts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Disable all price alerts for user"""
    
    updated = db.query(PriceAlert).filter(
        and_(PriceAlert.user_id == current_user.id, PriceAlert.is_active == True)
    ).update({"is_active": False})
    
    db.commit()
    
    return {
        "success": True,
        "message": f"Disabled {updated} alerts",
        "alerts_disabled": updated
    }


# ============================================
# ENABLE ALL ALERTS
# ============================================

@router.post("/enable-all-alerts")
async def enable_all_alerts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Enable all price alerts for user"""
    
    updated = db.query(PriceAlert).filter(
        and_(PriceAlert.user_id == current_user.id, PriceAlert.is_active == False)
    ).update({"is_active": True})
    
    db.commit()
    
    return {
        "success": True,
        "message": f"Enabled {updated} alerts",
        "alerts_enabled": updated
    }


# ============================================
# DELETE ALL ALERTS
# ============================================

@router.delete("/delete-all-alerts")
async def delete_all_alerts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete all price alerts for user"""
    
    deleted = db.query(PriceAlert).filter(
        PriceAlert.user_id == current_user.id
    ).delete()
    
    db.commit()
    
    return {
        "success": True,
        "message": f"Deleted {deleted} alerts",
        "alerts_deleted": deleted
    }


# ============================================
# CLEAR WISHLIST
# ============================================

@router.delete("/clear-wishlist")
async def clear_wishlist(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Clear all wishlist items"""
    
    deleted = db.query(Wishlist).filter(
        Wishlist.user_id == current_user.id
    ).delete()
    
    db.commit()
    
    return {
        "success": True,
        "message": f"Removed {deleted} items from wishlist",
        "items_deleted": deleted
    }


# ============================================
# EXPORT USER DATA (GDPR)
# ============================================

@router.get("/export-data")
async def export_user_data(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Export all user data (GDPR compliance)"""
    
    # Get wishlist items
    wishlists = db.query(Wishlist).filter(Wishlist.user_id == current_user.id).all()
    
    # Get alerts
    alerts = db.query(PriceAlert).filter(PriceAlert.user_id == current_user.id).all()
    
    return {
        "user": {
            "id": current_user.id,
            "name": current_user.name,
            "email": current_user.email,
            "role": current_user.role.value,
            "is_verified": current_user.is_verified,
            "created_at": current_user.created_at.isoformat() if current_user.created_at else None
        },
        "wishlist": [
            {
                "model_id": w.model_id,
                "created_at": w.created_at.isoformat() if w.created_at else None
            }
            for w in wishlists
        ],
        "price_alerts": [
            {
                "model_id": a.model_id,
                "target_price": a.target_price,
                "is_active": a.is_active,
                "created_at": a.created_at.isoformat() if a.created_at else None
            }
            for a in alerts
        ],
        "exported_at": datetime.now(timezone.utc).isoformat()
    }


# ============================================
# DELETE ACCOUNT
# ============================================

@router.delete("/delete-account")
async def delete_account(
    password: str,
    confirm: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Permanently delete user account"""
    
    if not confirm:
        raise HTTPException(
            status_code=400,
            detail="Please confirm account deletion by setting confirm=true"
        )
    
    # Verify password
    if not SecurityUtils.verify_password(password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect password")
    
    # Prevent admin self-deletion if only admin
    if current_user.role.value == "admin":
        admin_count = db.query(User).filter(User.role == "admin").count()
        if admin_count <= 1:
            raise HTTPException(
                status_code=400,
                detail="Cannot delete the only admin account"
            )
    
    # Delete user (cascades to wishlists, alerts, sessions)
    db.delete(current_user)
    db.commit()
    
    return {
        "success": True,
        "message": "Account deleted successfully"
    }


# ============================================
# UNSUBSCRIBE FROM EMAILS (via token)
# ============================================

@router.post("/unsubscribe")
async def unsubscribe(
    token: str = None,
    email: str = None,
    db: Session = Depends(get_db)
):
    """Unsubscribe from alert emails (can be used without login)"""
    
    user = None
    
    if token:
        # Decode unsubscribe token (if implementing token-based unsubscribe)
        # For now, just use email
        pass
    
    if email:
        user = db.query(User).filter(User.email == email.lower()).first()
    
    if not user:
        # Don't reveal if email exists
        return {"success": True, "message": "If the email exists, alerts have been disabled"}
    
    # Disable all alerts
    db.query(PriceAlert).filter(
        PriceAlert.user_id == user.id
    ).update({"is_active": False})
    
    db.commit()
    
    return {"success": True, "message": "Successfully unsubscribed from price alerts"}