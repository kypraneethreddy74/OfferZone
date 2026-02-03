"""
Wishlist API Routes
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text, and_
from typing import List

from db import get_db
from models import Wishlist, User
from auth.dependencies import get_current_active_user, get_current_verified_user
from .schemas import (
    WishlistItemCreate,
    WishlistItemResponse,
    WishlistResponse,
    WishlistStatusResponse
)

router = APIRouter(prefix="/wishlist", tags=["Wishlist"])


# ============================================
# GET WISHLIST
# ============================================

@router.get("", response_model=WishlistResponse)
async def get_wishlist(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get user's wishlist with product details"""
    
    # Query wishlist with product details
    query = text("""
        SELECT 
            w.id,
            w.model_id,
            w.created_at,
            MIN(p.full_name) as product_name,
            MIN(p.brand) as brand,
            MIN(p.image_url) as image_url,
            MIN(p.sale_price) as min_price,
            MAX(p.discount) as max_discount,
            COUNT(DISTINCT p.platform) as platform_count
        FROM wishlists w
        LEFT JOIN tv_platform_latest_master p ON w.model_id = p.model_id
        WHERE w.user_id = :user_id
        GROUP BY w.id, w.model_id, w.created_at
        ORDER BY w.created_at DESC
    """)
    
    result = db.execute(query, {"user_id": current_user.id})
    
    items = []
    for row in result:
        items.append(WishlistItemResponse(
            id=row.id,
            model_id=row.model_id,
            created_at=row.created_at,
            product_name=row.product_name,
            brand=row.brand,
            image_url=row.image_url,
            min_price=float(row.min_price) if row.min_price else None,
            max_discount=float(row.max_discount) if row.max_discount else None,
            platform_count=row.platform_count or 0
        ))
    
    return WishlistResponse(items=items, total=len(items))


# ============================================
# ADD TO WISHLIST
# ============================================

@router.post("", status_code=status.HTTP_201_CREATED)
async def add_to_wishlist(
    item: WishlistItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_verified_user)  # Requires verification
):
    """Add product to wishlist (requires verified email)"""
    
    # Check if already in wishlist
    existing = db.query(Wishlist).filter(
        and_(
            Wishlist.user_id == current_user.id,
            Wishlist.model_id == item.model_id
        )
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Product already in wishlist"
        )
    
    # Verify product exists
    product_check = db.execute(
        text("SELECT model_id FROM tv_platform_latest_master WHERE model_id = :model_id LIMIT 1"),
        {"model_id": item.model_id}
    ).fetchone()
    
    if not product_check:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Add to wishlist
    wishlist_item = Wishlist(
        user_id=current_user.id,
        model_id=item.model_id
    )
    db.add(wishlist_item)
    db.commit()
    db.refresh(wishlist_item)
    
    return {
        "success": True,
        "message": "Added to wishlist",
        "wishlist_id": wishlist_item.id
    }


# ============================================
# REMOVE FROM WISHLIST
# ============================================

@router.delete("/{model_id}")
async def remove_from_wishlist(
    model_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Remove product from wishlist"""
    
    wishlist_item = db.query(Wishlist).filter(
        and_(
            Wishlist.user_id == current_user.id,
            Wishlist.model_id == model_id
        )
    ).first()
    
    if not wishlist_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not in wishlist"
        )
    
    db.delete(wishlist_item)
    db.commit()
    
    return {
        "success": True,
        "message": "Removed from wishlist"
    }


# ============================================
# CHECK WISHLIST STATUS
# ============================================

@router.get("/check/{model_id}", response_model=WishlistStatusResponse)
async def check_wishlist_status(
    model_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Check if product is in user's wishlist"""
    
    wishlist_item = db.query(Wishlist).filter(
        and_(
            Wishlist.user_id == current_user.id,
            Wishlist.model_id == model_id
        )
    ).first()
    
    return WishlistStatusResponse(
        in_wishlist=wishlist_item is not None,
        wishlist_id=wishlist_item.id if wishlist_item else None
    )


# ============================================
# BULK CHECK WISHLIST STATUS
# ============================================

@router.post("/check-bulk")
async def check_wishlist_bulk(
    model_ids: List[str],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Check wishlist status for multiple products"""
    
    if len(model_ids) > 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum 100 products per request"
        )
    
    wishlist_items = db.query(Wishlist).filter(
        and_(
            Wishlist.user_id == current_user.id,
            Wishlist.model_id.in_(model_ids)
        )
    ).all()
    
    wishlisted_ids = {item.model_id for item in wishlist_items}
    
    return {
        "wishlisted": list(wishlisted_ids),
        "total": len(wishlisted_ids)
    }


# ============================================
# TOGGLE WISHLIST
# ============================================

@router.post("/toggle/{model_id}")
async def toggle_wishlist(
    model_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_verified_user)
):
    """Toggle product in wishlist (add if not present, remove if present)"""
    
    existing = db.query(Wishlist).filter(
        and_(
            Wishlist.user_id == current_user.id,
            Wishlist.model_id == model_id
        )
    ).first()
    
    if existing:
        # Remove
        db.delete(existing)
        db.commit()
        return {
            "success": True,
            "action": "removed",
            "in_wishlist": False,
            "message": "Removed from wishlist"
        }
    else:
        # Add
        wishlist_item = Wishlist(
            user_id=current_user.id,
            model_id=model_id
        )
        db.add(wishlist_item)
        db.commit()
        return {
            "success": True,
            "action": "added",
            "in_wishlist": True,
            "message": "Added to wishlist"
        }


# ============================================
# WISHLIST COUNT
# ============================================

@router.get("/count")
async def get_wishlist_count(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get total items in wishlist"""
    
    count = db.query(Wishlist).filter(
        Wishlist.user_id == current_user.id
    ).count()
    
    return {"count": count}