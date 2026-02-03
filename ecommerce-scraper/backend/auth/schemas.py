"""
Pydantic Schemas for Authentication
"""

from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict
from typing import Optional
from datetime import datetime
from enum import Enum
import re


class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"


# ============================================
# REQUEST SCHEMAS
# ============================================

class UserRegisterRequest(BaseModel):
    """Schema for user registration"""
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    confirm_password: str

    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if not v.strip():
            raise ValueError('Name cannot be empty')
        return v.strip()

    @field_validator('password')
    @classmethod
    def validate_password_strength(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one digit')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password must contain at least one special character')
        return v

    @field_validator('confirm_password')
    @classmethod
    def passwords_match(cls, v, info):
        if 'password' in info.data and v != info.data['password']:
            raise ValueError('Passwords do not match')
        return v


class UserLoginRequest(BaseModel):
    """Schema for user login"""
    email: EmailStr
    password: str


# ============================================
# NEW: EMAIL VERIFICATION SCHEMAS
# ============================================

class ResendVerificationRequest(BaseModel):
    """Schema for resending verification email"""
    email: EmailStr


class VerifyEmailRequest(BaseModel):
    """Schema for email verification"""
    token: str


# ============================================
# NEW: PASSWORD RESET SCHEMAS
# ============================================

class ForgotPasswordRequest(BaseModel):
    """Schema for forgot password request"""
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    """Schema for password reset"""
    token: str
    password: str = Field(..., min_length=8, max_length=128)
    confirm_password: str

    @field_validator('password')
    @classmethod
    def validate_password_strength(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one digit')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password must contain at least one special character')
        return v

    @field_validator('confirm_password')
    @classmethod
    def passwords_match(cls, v, info):
        if 'password' in info.data and v != info.data['password']:
            raise ValueError('Passwords do not match')
        return v


# ============================================
# RESPONSE SCHEMAS
# ============================================

class UserResponse(BaseModel):
    """Schema for user response"""
    id: int
    name: str
    email: str
    role: UserRole
    is_active: bool
    is_verified: bool  # NEW FIELD
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AuthResponse(BaseModel):
    """Schema for authentication response"""
    success: bool
    message: str
    user: Optional[UserResponse] = None
    requires_verification: bool = False  # NEW FIELD


class MessageResponse(BaseModel):
    """Generic message response"""
    success: bool
    message: str


class SessionInfo(BaseModel):
    """Session information"""
    id: int
    user_agent: Optional[str]
    ip_address: Optional[str]
    created_at: Optional[datetime]
    expires_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)