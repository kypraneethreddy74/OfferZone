from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional


# ============================
# PRODUCT RESPONSE
# ============================
class TVProductOut(BaseModel):
    platform: str
    brand: str
    model_id: str
    full_name: str
    display_type: Optional[str] = None
    sale_price: float
    original_cost: Optional[float] = None
    discount: Optional[float] = None
    rating: Optional[float] = None
    stock_status: str
    scraped_at: Optional[datetime] = None
    image_url: Optional[str] = None

    model_config = ConfigDict(
        from_attributes=True,
        protected_namespaces=()  # ✅ ADDED
    )


# ============================
# BRAND ANALYTICS
# ============================
class BrandAnalyticsOut(BaseModel):
    brand: str
    total_models: int
    total_listings: int
    in_stock_count: int

    model_config = ConfigDict(
        from_attributes=True,
        protected_namespaces=()  # ✅ ADDED
    )


# ============================
# PLATFORM ANALYTICS
# ============================
class PlatformAnalyticsOut(BaseModel):
    platform: str
    total_listings: int
    unique_models: int
    in_stock_count: int

    model_config = ConfigDict(
        from_attributes=True,
        protected_namespaces=()  # ✅ ADDED
    )