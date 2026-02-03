"""
FastAPI Dependencies for Authentication
"""

from fastapi import Depends, HTTPException, status, Request, Cookie
from sqlalchemy.orm import Session
from typing import Optional
from db import get_db
from models import User, UserRole
from .security import SecurityUtils


class AuthError(HTTPException):
    """Custom auth error"""
    def __init__(self, detail: str, status_code: int = status.HTTP_401_UNAUTHORIZED):
        super().__init__(
            status_code=status_code,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"}
        )


async def get_token_from_cookie(
    access_token: Optional[str] = Cookie(None, alias="access_token")
) -> str:
    """Extract access token from cookie"""
    if not access_token:
        raise AuthError("Not authenticated")
    return access_token


async def get_current_user(
    token: str = Depends(get_token_from_cookie),
    db: Session = Depends(get_db)
) -> User:
    """Get current user from token"""
    payload = SecurityUtils.decode_access_token(token)
    
    if not payload:
        raise AuthError("Invalid or expired token")
    
    user_id = payload.get("sub")
    if not user_id:
        raise AuthError("Invalid token")
    
    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        raise AuthError("User not found")
    
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get current active user"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account deactivated"
        )
    return current_user


# ============================================
# NEW: VERIFICATION CHECK DEPENDENCIES
# ============================================

async def get_current_verified_user(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """Get current verified user - use this for features requiring verification"""
    if not current_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email not verified. Please verify your email to access this feature."
        )
    return current_user


async def require_admin(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """Require admin role"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


async def require_user(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """Require authenticated user"""
    return current_user


# ============================================
# RATE LIMITER
# ============================================

class RateLimiter:
    def __init__(self, max_requests: int = 5, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: dict = {}
    
    async def check(self, request: Request) -> bool:
        import time
        client_ip = request.client.host if request.client else "unknown"
        current_time = time.time()
        
        # Clean old entries
        self.requests = {
            k: v for k, v in self.requests.items()
            if current_time - v["start"] < self.window_seconds
        }
        
        if client_ip not in self.requests:
            self.requests[client_ip] = {"count": 1, "start": current_time}
            return True
        
        if self.requests[client_ip]["count"] >= self.max_requests:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many requests. Please try again later."
            )
        
        self.requests[client_ip]["count"] += 1
        return True


login_rate_limiter = RateLimiter(max_requests=5, window_seconds=60)
register_rate_limiter = RateLimiter(max_requests=3, window_seconds=60)
verification_rate_limiter = RateLimiter(max_requests=3, window_seconds=60)
password_reset_rate_limiter = RateLimiter(max_requests=3, window_seconds=60)