"""
Authentication Module
"""

from .routes import router as auth_router
from .dependencies import (
    get_current_user,
    get_current_active_user,
    get_current_verified_user,
    require_admin,
    require_user
)
from .security import SecurityUtils, SecurityConfig

__all__ = [
    "auth_router",
    "get_current_user",
    "get_current_active_user",
    "get_current_verified_user",
    "require_admin",
    "require_user",
    "SecurityUtils",
    "SecurityConfig"
]