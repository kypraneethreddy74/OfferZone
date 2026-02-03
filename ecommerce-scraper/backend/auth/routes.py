"""
Authentication API Routes
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request, Response, BackgroundTasks
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime, timezone

from db import get_db
from models import User, RefreshSession, UserRole, EmailVerificationToken
from .schemas import (
    UserRegisterRequest, UserLoginRequest, UserResponse,
    AuthResponse, MessageResponse, ResendVerificationRequest,
    VerifyEmailRequest, ForgotPasswordRequest, ResetPasswordRequest
)
from .security import SecurityUtils
from .dependencies import (
    get_current_active_user, get_current_verified_user,
    login_rate_limiter, register_rate_limiter,
    verification_rate_limiter, password_reset_rate_limiter
)
from email_service import EmailService

router = APIRouter(prefix="/auth", tags=["Authentication"])


def get_client_info(request: Request) -> tuple:
    """Extract client info"""
    client_ip = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("user-agent", "unknown")[:500]
    return client_ip, user_agent


def set_auth_cookies(response: Response, access_token: str, refresh_token: str):
    """Set auth cookies"""
    access_settings = SecurityUtils.get_cookie_settings(is_access_token=True)
    response.set_cookie(key="access_token", value=access_token, **access_settings)
    
    refresh_settings = SecurityUtils.get_cookie_settings(is_access_token=False)
    response.set_cookie(key="refresh_token", value=refresh_token, **refresh_settings)


def clear_auth_cookies(response: Response):
    """Clear auth cookies"""
    response.delete_cookie(key="access_token", path="/")
    response.delete_cookie(key="refresh_token", path="/auth")


def create_verification_token(db: Session, user: User) -> str:
    """Create and store a verification token for a user"""
    # Invalidate any existing unused tokens
    db.query(EmailVerificationToken).filter(
        and_(
            EmailVerificationToken.user_id == user.id,
            EmailVerificationToken.is_used == False
        )
    ).update({"is_used": True})
    
    # Create new token
    token = SecurityUtils.generate_verification_token()
    verification_token = EmailVerificationToken(
        user_id=user.id,
        token=token,
        expires_at=SecurityUtils.get_verification_token_expiry()
    )
    db.add(verification_token)
    db.commit()
    
    return token


# ============================================
# REGISTRATION
# ============================================

@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(
    request: Request,
    user_data: UserRegisterRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    _: bool = Depends(register_rate_limiter.check)
):
    """Register new user with email verification"""
    # Check existing email
    existing = db.query(User).filter(User.email == user_data.email.lower()).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )
    
    # Create user (unverified)
    new_user = User(
        name=user_data.name,
        email=user_data.email.lower(),
        hashed_password=SecurityUtils.hash_password(user_data.password),
        role=UserRole.USER,
        is_active=True,
        is_verified=False  # NEW: Start unverified
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Create verification token and send email
    verification_token = create_verification_token(db, new_user)
    
    # Send verification email in background
    background_tasks.add_task(
        EmailService.send_verification_email,
        new_user.email,
        new_user.name,
        verification_token
    )
    
    # Create auth tokens
    client_ip, user_agent = get_client_info(request)
    
    access_token, _ = SecurityUtils.create_access_token(
        user_id=new_user.id,
        email=new_user.email,
        role=new_user.role.value
    )
    
    refresh_token, refresh_expires, _ = SecurityUtils.create_refresh_token(
        user_id=new_user.id,
        email=new_user.email,
        role=new_user.role.value
    )
    
    # Store refresh session
    refresh_session = RefreshSession(
        user_id=new_user.id,
        hashed_refresh_token=SecurityUtils.hash_token(refresh_token),
        expires_at=refresh_expires,
        user_agent=user_agent,
        ip_address=client_ip
    )
    db.add(refresh_session)
    db.commit()
    
    # Response
    response_data = AuthResponse(
        success=True,
        message="Registration successful. Please check your email to verify your account.",
        user=UserResponse.model_validate(new_user),
        requires_verification=True
    )
    
    response = JSONResponse(
        content=response_data.model_dump(mode='json'),
        status_code=status.HTTP_201_CREATED
    )
    set_auth_cookies(response, access_token, refresh_token)
    
    return response


# ============================================
# EMAIL VERIFICATION
# ============================================
@router.post("/verify-email", response_model=MessageResponse)
async def verify_email(
    request: VerifyEmailRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Verify email with token"""
    # Find token
    token_record = db.query(EmailVerificationToken).filter(
        EmailVerificationToken.token == request.token
    ).first()
    
    if not token_record:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid verification token. Please request a new one."
        )
    
    # Get user first
    user = db.query(User).filter(User.id == token_record.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check if user is already verified
    if user.is_verified:
        return MessageResponse(
            success=True, 
            message="Email is already verified. You can log in now."
        )
    
    # Check if token is used
    if token_record.is_used:
        # If user is verified, it's fine
        if user.is_verified:
            return MessageResponse(
                success=True, 
                message="Email is already verified. You can log in now."
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This verification link has already been used. Please request a new one."
        )
    
    # Check if token is expired
    if token_record.expires_at.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Verification link has expired. Please request a new one."
        )
    
    # Verify user
    user.is_verified = True
    user.verified_at = datetime.now(timezone.utc)
    
    # Mark token as used
    token_record.is_used = True
    token_record.used_at = datetime.now(timezone.utc)
    
    db.commit()
    
    # Send success email in background
    background_tasks.add_task(
        EmailService.send_verification_success_email,
        user.email,
        user.name
    )
    
    return MessageResponse(success=True, message="Email verified successfully! 🎉")


@router.post("/resend-verification", response_model=MessageResponse)
async def resend_verification(
    request: Request,
    data: ResendVerificationRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    _: bool = Depends(verification_rate_limiter.check)
):
    """Resend verification email"""
    user = db.query(User).filter(User.email == data.email.lower()).first()
    
    # Always return success to prevent email enumeration
    if not user:
        return MessageResponse(
            success=True,
            message="If an account exists with this email, a verification link has been sent."
        )
    
    if user.is_verified:
        return MessageResponse(
            success=True,
            message="Email is already verified. You can log in."
        )
    
    # Create new verification token
    verification_token = create_verification_token(db, user)
    
    # Send email in background
    background_tasks.add_task(
        EmailService.send_verification_email,
        user.email,
        user.name,
        verification_token
    )
    
    return MessageResponse(
        success=True,
        message="If an account exists with this email, a verification link has been sent."
    )


# ============================================
# PASSWORD RESET
# ============================================

@router.post("/forgot-password", response_model=MessageResponse)
async def forgot_password(
    request: Request,
    data: ForgotPasswordRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    _: bool = Depends(password_reset_rate_limiter.check)
):
    """Request password reset"""
    user = db.query(User).filter(User.email == data.email.lower()).first()
    
    # Always return success to prevent email enumeration
    if not user:
        return MessageResponse(
            success=True,
            message="If an account exists with this email, a password reset link has been sent."
        )
    
    if not user.is_active:
        return MessageResponse(
            success=True,
            message="If an account exists with this email, a password reset link has been sent."
        )
    
    # Generate reset token
    reset_token = SecurityUtils.generate_password_reset_token()
    user.password_reset_token = SecurityUtils.hash_token(reset_token)
    user.password_reset_expires = SecurityUtils.get_password_reset_token_expiry()
    db.commit()
    
    # Send email in background
    background_tasks.add_task(
        EmailService.send_password_reset_email,
        user.email,
        user.name,
        reset_token
    )
    
    return MessageResponse(
        success=True,
        message="If an account exists with this email, a password reset link has been sent."
    )


@router.post("/reset-password", response_model=MessageResponse)
async def reset_password(
    data: ResetPasswordRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Reset password with token"""
    hashed_token = SecurityUtils.hash_token(data.token)
    
    user = db.query(User).filter(
        User.password_reset_token == hashed_token
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )
    
    if not user.password_reset_expires:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )
    
    if user.password_reset_expires.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
        # Clear expired token
        user.password_reset_token = None
        user.password_reset_expires = None
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Reset token has expired. Please request a new one."
        )
    
    # Update password
    user.hashed_password = SecurityUtils.hash_password(data.password)
    user.password_reset_token = None
    user.password_reset_expires = None
    
    # Revoke all refresh sessions for security
    db.query(RefreshSession).filter(
        RefreshSession.user_id == user.id
    ).update({"is_revoked": True})
    
    db.commit()
    
    # Send confirmation email
    background_tasks.add_task(
        EmailService.send_password_changed_email,
        user.email,
        user.name
    )
    
    return MessageResponse(
        success=True,
        message="Password reset successfully. You can now log in with your new password."
    )


# ============================================
# LOGIN
# ============================================

@router.post("/login", response_model=AuthResponse)
async def login(
    request: Request,
    credentials: UserLoginRequest,
    db: Session = Depends(get_db),
    _: bool = Depends(login_rate_limiter.check)
):
    """Login user"""
    user = db.query(User).filter(User.email == credentials.email.lower()).first()
    
    if not user or not SecurityUtils.verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account deactivated"
        )
    
    # Create tokens
    client_ip, user_agent = get_client_info(request)
    
    access_token, _ = SecurityUtils.create_access_token(
        user_id=user.id,
        email=user.email,
        role=user.role.value
    )
    
    refresh_token, refresh_expires, _ = SecurityUtils.create_refresh_token(
        user_id=user.id,
        email=user.email,
        role=user.role.value
    )
    
    # Store refresh session
    refresh_session = RefreshSession(
        user_id=user.id,
        hashed_refresh_token=SecurityUtils.hash_token(refresh_token),
        expires_at=refresh_expires,
        user_agent=user_agent,
        ip_address=client_ip
    )
    db.add(refresh_session)
    db.commit()
    
    # Response with verification status
    response_data = AuthResponse(
        success=True,
        message="Login successful" if user.is_verified else "Login successful. Please verify your email.",
        user=UserResponse.model_validate(user),
        requires_verification=not user.is_verified
    )
    
    response = JSONResponse(content=response_data.model_dump(mode='json'))
    set_auth_cookies(response, access_token, refresh_token)
    
    return response


# ============================================
# TOKEN REFRESH (Continued)
# ============================================

@router.post("/refresh")
async def refresh_tokens(request: Request, db: Session = Depends(get_db)):
    """Refresh tokens with rotation"""
    refresh_token = request.cookies.get("refresh_token")
    
    if not refresh_token:
        raise HTTPException(status_code=401, detail="No refresh token")
    
    payload = SecurityUtils.decode_refresh_token(refresh_token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    
    user_id = int(payload.get("sub"))
    hashed_token = SecurityUtils.hash_token(refresh_token)
    
    # Find session
    session = db.query(RefreshSession).filter(
        and_(
            RefreshSession.hashed_refresh_token == hashed_token,
            RefreshSession.user_id == user_id
        )
    ).first()
    
    if not session:
        # Potential reuse attack - revoke all sessions
        db.query(RefreshSession).filter(
            RefreshSession.user_id == user_id
        ).update({"is_revoked": True})
        db.commit()
        raise HTTPException(status_code=401, detail="Invalid token - sessions revoked")
    
    if session.is_revoked:
        # Token reuse detected
        db.query(RefreshSession).filter(
            RefreshSession.user_id == user_id
        ).update({"is_revoked": True})
        db.commit()
        raise HTTPException(status_code=401, detail="Token reuse detected")
    
    if session.expires_at.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
        session.is_revoked = True
        db.commit()
        raise HTTPException(status_code=401, detail="Token expired")
    
    # Get user
    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.is_active:
        session.is_revoked = True
        db.commit()
        raise HTTPException(status_code=401, detail="User not found")
    
    # Revoke old token
    session.is_revoked = True
    
    # Create new tokens
    client_ip, user_agent = get_client_info(request)
    
    new_access_token, _ = SecurityUtils.create_access_token(
        user_id=user.id, email=user.email, role=user.role.value
    )
    
    new_refresh_token, refresh_expires, _ = SecurityUtils.create_refresh_token(
        user_id=user.id, email=user.email, role=user.role.value
    )
    
    # Create new session
    new_session = RefreshSession(
        user_id=user.id,
        hashed_refresh_token=SecurityUtils.hash_token(new_refresh_token),
        expires_at=refresh_expires,
        user_agent=user_agent,
        ip_address=client_ip
    )
    db.add(new_session)
    db.commit()
    
    response = JSONResponse(content={"success": True, "message": "Tokens refreshed"})
    set_auth_cookies(response, new_access_token, new_refresh_token)
    
    return response


# ============================================
# LOGOUT
# ============================================

@router.post("/logout")
async def logout(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Logout current session"""
    refresh_token = request.cookies.get("refresh_token")
    
    if refresh_token:
        hashed_token = SecurityUtils.hash_token(refresh_token)
        session = db.query(RefreshSession).filter(
            and_(
                RefreshSession.hashed_refresh_token == hashed_token,
                RefreshSession.user_id == current_user.id
            )
        ).first()
        
        if session:
            session.is_revoked = True
            db.commit()
    
    response = JSONResponse(content={"success": True, "message": "Logged out"})
    clear_auth_cookies(response)
    
    return response


@router.post("/logout-all")
async def logout_all(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Logout all sessions"""
    db.query(RefreshSession).filter(
        RefreshSession.user_id == current_user.id
    ).update({"is_revoked": True})
    db.commit()
    
    response = JSONResponse(content={"success": True, "message": "All sessions logged out"})
    clear_auth_cookies(response)
    
    return response


# ============================================
# USER INFO
# ============================================

@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_active_user)):
    """Get current user info"""
    return UserResponse.model_validate(current_user)


@router.get("/sessions")
async def get_sessions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get active sessions"""
    sessions = db.query(RefreshSession).filter(
        and_(
            RefreshSession.user_id == current_user.id,
            RefreshSession.is_revoked == False,
            RefreshSession.expires_at > datetime.now(timezone.utc)
        )
    ).all()
    
    return {
        "sessions": [
            {
                "id": s.id,
                "user_agent": s.user_agent,
                "ip_address": s.ip_address,
                "created_at": s.created_at.isoformat() if s.created_at else None,
                "expires_at": s.expires_at.isoformat() if s.expires_at else None
            }
            for s in sessions
        ],
        "total": len(sessions)
    }


# ============================================
# VERIFICATION STATUS CHECK
# ============================================

@router.get("/verification-status")
async def get_verification_status(
    current_user: User = Depends(get_current_active_user)
):
    """Check if current user is verified"""
    return {
        "is_verified": current_user.is_verified,
        "email": current_user.email,
        "verified_at": current_user.verified_at.isoformat() if current_user.verified_at else None
    }