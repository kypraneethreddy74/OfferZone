"""
Wishlist Schemas
"""

from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


class WishlistItemCreate(BaseModel):
    """Add item to wishlist"""
    model_id: str


class WishlistItemResponse(BaseModel):
    """Wishlist item response"""
    id: int
    model_id: str
    created_at: datetime
    
    # Product details (joined)
    product_name: Optional[str] = None
    brand: Optional[str] = None
    image_url: Optional[str] = None
    min_price: Optional[float] = None
    max_discount: Optional[float] = None
    platform_count: Optional[int] = None

    class Config:
        from_attributes = True


class WishlistResponse(BaseModel):
    """Full wishlist response"""
    items: List[WishlistItemResponse]
    total: int


class WishlistStatusResponse(BaseModel):
    """Check if product is in wishlist"""
    in_wishlist: bool
    wishlist_id: Optional[int] = None