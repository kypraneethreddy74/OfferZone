"""
Security utilities for JWT and password handling
"""

import os
import secrets
import hashlib
from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple
from jose import jwt, JWTError, ExpiredSignatureError
from passlib.context import CryptContext
from dotenv import load_dotenv

load_dotenv()


class SecurityConfig:
    """Security configuration"""
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "change-this-secret")
    JWT_REFRESH_SECRET_KEY: str = os.getenv("JWT_REFRESH_SECRET_KEY", "change-this-refresh")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "15"))
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))
    COOKIE_SECURE: bool = os.getenv("COOKIE_SECURE", "False").lower() == "true"
    
    # NEW: Verification token settings
    VERIFICATION_TOKEN_EXPIRE_HOURS: int = int(os.getenv("VERIFICATION_TOKEN_EXPIRE_HOURS", "24"))
    PASSWORD_RESET_TOKEN_EXPIRE_HOURS: int = int(os.getenv("PASSWORD_RESET_TOKEN_EXPIRE_HOURS", "1"))


class SecurityUtils:
    """Centralized security utilities"""
    
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    @classmethod
    def hash_password(cls, password: str) -> str:
        """Hash a password"""
        return cls.pwd_context.hash(password)

    @classmethod
    def verify_password(cls, plain_password: str, hashed_password: str) -> bool:
        """Verify password"""
        try:
            return cls.pwd_context.verify(plain_password, hashed_password)
        except Exception:
            return False

    @staticmethod
    def generate_token_id() -> str:
        """Generate unique token ID"""
        return secrets.token_urlsafe(32)

    @staticmethod
    def hash_token(token: str) -> str:
        """Hash a refresh token for DB storage"""
        return hashlib.sha256(token.encode()).hexdigest()

    # ============================================
    # NEW: VERIFICATION TOKEN METHODS
    # ============================================

    @staticmethod
    def generate_verification_token() -> str:
        """Generate a secure verification token"""
        return secrets.token_urlsafe(64)

    @staticmethod
    def generate_password_reset_token() -> str:
        """Generate a secure password reset token"""
        return secrets.token_urlsafe(64)

    @classmethod
    def get_verification_token_expiry(cls) -> datetime:
        """Get expiry time for verification token"""
        return datetime.now(timezone.utc) + timedelta(
            hours=SecurityConfig.VERIFICATION_TOKEN_EXPIRE_HOURS
        )

    @classmethod
    def get_password_reset_token_expiry(cls) -> datetime:
        """Get expiry time for password reset token"""
        return datetime.now(timezone.utc) + timedelta(
            hours=SecurityConfig.PASSWORD_RESET_TOKEN_EXPIRE_HOURS
        )

    # ============================================
    # EXISTING JWT METHODS
    # ============================================

    @classmethod
    def create_access_token(
        cls,
        user_id: int,
        email: str,
        role: str,
        expires_delta: Optional[timedelta] = None
    ) -> Tuple[str, datetime]:
        """Create access token"""
        now = datetime.now(timezone.utc)
        expire = now + (expires_delta or timedelta(
            minutes=SecurityConfig.ACCESS_TOKEN_EXPIRE_MINUTES
        ))

        payload = {
            "sub": str(user_id),
            "email": email,
            "role": role,
            "type": "access",
            "exp": expire,
            "iat": now,
            "jti": cls.generate_token_id()
        }

        token = jwt.encode(
            payload,
            SecurityConfig.JWT_SECRET_KEY,
            algorithm=SecurityConfig.JWT_ALGORITHM
        )
        return token, expire

    @classmethod
    def create_refresh_token(
        cls,
        user_id: int,
        email: str,
        role: str,
        expires_delta: Optional[timedelta] = None
    ) -> Tuple[str, datetime, str]:
        """Create refresh token"""
        now = datetime.now(timezone.utc)
        expire = now + (expires_delta or timedelta(
            days=SecurityConfig.REFRESH_TOKEN_EXPIRE_DAYS
        ))

        token_id = cls.generate_token_id()
        payload = {
            "sub": str(user_id),
            "email": email,
            "role": role,
            "type": "refresh",
            "exp": expire,
            "iat": now,
            "jti": token_id
        }

        token = jwt.encode(
            payload,
            SecurityConfig.JWT_REFRESH_SECRET_KEY,
            algorithm=SecurityConfig.JWT_ALGORITHM
        )
        return token, expire, token_id

    @classmethod
    def decode_access_token(cls, token: str) -> Optional[dict]:
        """Decode access token"""
        try:
            payload = jwt.decode(
                token,
                SecurityConfig.JWT_SECRET_KEY,
                algorithms=[SecurityConfig.JWT_ALGORITHM]
            )
            if payload.get("type") != "access":
                return None
            return payload
        except (ExpiredSignatureError, JWTError):
            return None

    @classmethod
    def decode_refresh_token(cls, token: str) -> Optional[dict]:
        """Decode refresh token"""
        try:
            payload = jwt.decode(
                token,
                SecurityConfig.JWT_REFRESH_SECRET_KEY,
                algorithms=[SecurityConfig.JWT_ALGORITHM]
            )
            if payload.get("type") != "refresh":
                return None
            return payload
        except (ExpiredSignatureError, JWTError):
            return None

    @staticmethod
    def get_cookie_settings(is_access_token: bool = True) -> dict:
        """Get secure cookie settings"""
        max_age = (
            SecurityConfig.ACCESS_TOKEN_EXPIRE_MINUTES * 60
            if is_access_token
            else SecurityConfig.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
        )
        return {
            "httponly": True,
            "secure": SecurityConfig.COOKIE_SECURE,
            "samesite": "lax",
            "max_age": max_age,
            "path": "/" if is_access_token else "/auth"
        }