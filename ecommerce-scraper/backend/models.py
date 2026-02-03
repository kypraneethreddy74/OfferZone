"""
Database Models for OfferZone TV Price Intelligence
Includes Authentication and Product Models
"""

from sqlalchemy import (
    Column, String, Float, BigInteger, DateTime, Integer,
    Boolean, ForeignKey, Index, Enum as SQLEnum, Text
)
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func
import enum

Base = declarative_base()


# ============================================
# AUTHENTICATION MODELS
# ============================================

class UserRole(str, enum.Enum):
    """User roles for authorization"""
    ADMIN = "admin"
    USER = "user"


class User(Base):
    """User model for authentication"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(SQLEnum(UserRole), default=UserRole.USER, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # ========== NEW: Email Verification Fields ==========
    is_verified = Column(Boolean, default=False, nullable=False)
    verified_at = Column(DateTime(timezone=True), nullable=True)
    
    # ========== NEW: Password Reset Fields ==========
    password_reset_token = Column(String(255), nullable=True, index=True)
    password_reset_expires = Column(DateTime(timezone=True), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    refresh_sessions = relationship(
        "RefreshSession",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    
    # ========== NEW: Verification Tokens Relationship ==========
    verification_tokens = relationship(
        "EmailVerificationToken",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    
    wishlists = relationship(
        "Wishlist",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    
    price_alerts = relationship(
        "PriceAlert",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, role={self.role}, verified={self.is_verified})>"


class RefreshSession(Base):
    """Refresh token sessions for secure token rotation"""
    __tablename__ = "refresh_sessions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    hashed_refresh_token = Column(String(255), nullable=False, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    is_revoked = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    user_agent = Column(String(500), nullable=True)
    ip_address = Column(String(45), nullable=True)

    # Relationships
    user = relationship("User", back_populates="refresh_sessions")

    # Indexes
    __table_args__ = (
        Index('idx_refresh_session_user_active', 'user_id', 'is_revoked'),
        Index('idx_refresh_session_token', 'hashed_refresh_token'),
    )

    def __repr__(self):
        return f"<RefreshSession(id={self.id}, user_id={self.user_id})>"


# ============================================
# NEW: EMAIL VERIFICATION TOKEN MODEL
# ============================================

class EmailVerificationToken(Base):
    """Email verification tokens"""
    __tablename__ = "email_verification_tokens"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    token = Column(String(255), nullable=False, unique=True, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    is_used = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    used_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    user = relationship("User", back_populates="verification_tokens")

    # Indexes
    __table_args__ = (
        Index('idx_verification_token', 'token'),
        Index('idx_verification_user', 'user_id', 'is_used'),
    )

    def __repr__(self):
        return f"<EmailVerificationToken(id={self.id}, user_id={self.user_id})>"


# ============================================
# WISHLIST MODEL
# ============================================

class Wishlist(Base):
    """User wishlist for favorite products"""
    __tablename__ = "wishlists"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    model_id = Column(String(100), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="wishlists")

    # Unique constraint
    __table_args__ = (
        Index('idx_wishlist_user', 'user_id'),
        Index('idx_wishlist_model', 'model_id'),
    )

    def __repr__(self):
        return f"<Wishlist(user_id={self.user_id}, model_id={self.model_id})>"

# ============================================
# EXISTING TV PRODUCT MODELS (UNCHANGED)
# ============================================

class TVPlatformLatest(Base):
    __tablename__ = "tv_platform_latest_master"

    platform = Column(String(50), primary_key=True)
    model_id = Column(String(100), primary_key=True)
    brand = Column(String(100))
    full_name = Column(String(255))
    display_type = Column(String(50))
    sale_price = Column(Float)
    original_cost = Column(Float)
    discount = Column(Float)
    stock_status = Column(String(50))
    scraped_at = Column(DateTime)
    product_url = Column(String(500))
    rating = Column(Float)
    image_url = Column("image_url", String(500))


class TVProductMaster(Base):
    __tablename__ = "tv_product_master"

    model_id = Column(String(100), primary_key=True)
    brand = Column(String(100))
    full_name = Column(String(255))
    display_type = Column(String(50))


class TVBrandMaster(Base):
    __tablename__ = "tv_brand_master"

    brand = Column(String(100), primary_key=True)
    total_models = Column(BigInteger)
    total_listings = Column(BigInteger)
    in_stock_count = Column(BigInteger)


class TVPlatformMaster(Base):
    __tablename__ = "tv_platform_master"

    platform = Column(String(100), primary_key=True)
    total_listings = Column(BigInteger)
    unique_models = Column(BigInteger)
    in_stock_count = Column(BigInteger)
    
    
# ============================================
# PRICE ALERT MODELS
# ============================================

class PriceAlert(Base):
    """Price alert for products"""
    __tablename__ = "price_alerts"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    model_id = Column(String(100), nullable=False)
    target_price = Column(Float, nullable=False)
    current_price = Column(Float, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    is_triggered = Column(Boolean, default=False, nullable=False)
    last_checked_at = Column(DateTime(timezone=True), nullable=True)
    last_notified_at = Column(DateTime(timezone=True), nullable=True)
    last_notified_price = Column(Float, nullable=True)
    trigger_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="price_alerts")
    notifications = relationship("AlertNotification", back_populates="alert", cascade="all, delete-orphan")

    __table_args__ = (
        Index('idx_alert_user', 'user_id'),
        Index('idx_alert_model', 'model_id'),
        Index('idx_alert_active', 'is_active', 'is_triggered'),
    )

    def __repr__(self):
        return f"<PriceAlert(user_id={self.user_id}, model_id={self.model_id}, target={self.target_price})>"


class AlertNotification(Base):
    """History of alert notifications sent"""
    __tablename__ = "alert_notifications"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    alert_id = Column(Integer, ForeignKey("price_alerts.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    model_id = Column(String(100), nullable=False)
    target_price = Column(Float, nullable=False)
    triggered_price = Column(Float, nullable=False)
    platform = Column(String(50), nullable=False)
    email_sent = Column(Boolean, default=False)
    email_sent_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    alert = relationship("PriceAlert", back_populates="notifications")

    def __repr__(self):
        return f"<AlertNotification(alert_id={self.alert_id}, price={self.triggered_price})>"