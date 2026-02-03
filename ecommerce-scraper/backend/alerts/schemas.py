"""
Price Alert Schemas
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List


class AlertCreate(BaseModel):
    """Create price alert"""
    model_id: str
    target_price: float = Field(..., gt=0, description="Target price must be positive")


class AlertUpdate(BaseModel):
    """Update price alert"""
    target_price: Optional[float] = Field(None, gt=0)
    is_active: Optional[bool] = None


class AlertResponse(BaseModel):
    """Alert response with product details"""
    id: int
    model_id: str
    target_price: float
    current_price: Optional[float]
    is_active: bool
    is_triggered: bool
    trigger_count: int
    created_at: datetime
    last_notified_at: Optional[datetime]
    
    # Product details
    product_name: Optional[str] = None
    brand: Optional[str] = None
    image_url: Optional[str] = None
    min_price: Optional[float] = None
    best_platform: Optional[str] = None

    class Config:
        from_attributes = True


class AlertListResponse(BaseModel):
    """List of alerts"""
    alerts: List[AlertResponse]
    total: int
    active_count: int
    triggered_count: int


class AlertStatusResponse(BaseModel):
    """Check alert status for a product"""
    has_alert: bool
    alert_id: Optional[int] = None
    target_price: Optional[float] = None
    is_active: Optional[bool] = None


class AlertNotificationResponse(BaseModel):
    """Alert notification history"""
    id: int
    model_id: str
    target_price: float
    triggered_price: float
    platform: str
    created_at: datetime
    product_name: Optional[str] = None