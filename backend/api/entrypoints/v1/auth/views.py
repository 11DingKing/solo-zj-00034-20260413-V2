import os
from fastapi import APIRouter, HTTPException, status
from loguru import logger

from api.entrypoints.v1.auth.schema import (
    LoginRequest,
    RegisterRequest,
    PasswordResetRequest,
    PasswordResetConfirm,
    AuthResponse,
    UserResponse,
    TokenValidateResponse,
)
from api.models.user import UserCreate
from api.services.user_service import UserService, PasswordService
from api.services.password_reset_service import PasswordResetService
from api.services.email_service import EmailService

router = APIRouter()


def get_frontend_url() -> str:
    return os.getenv("FRONTEND_URL", "http://localhost:5173")


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(request: RegisterRequest):
    try:
        user_create = UserCreate(email=request.email, username=request.username, password=request.password)
        user = UserService.create_user(user_create)
        return AuthResponse(
            success=True,
            message="User registered successfully",
            user=UserResponse(id=user.id, email=user.email, username=user.username, is_active=user.is_active),
        )
    except ValueError as e:
        error_message = str(e)
        if "already exists" in error_message:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=error_message,
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_message,
        )


@router.post("/login", response_model=AuthResponse)
async def login(request: LoginRequest):
    user = UserService.authenticate_user(request.email, request.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    return AuthResponse(
        success=True,
        message="Login successful",
        user=UserResponse(id=user.id, email=user.email, username=user.username, is_active=user.is_active),
    )


@router.post("/password-reset/request", response_model=AuthResponse)
async def request_password_reset(request: PasswordResetRequest):
    user = UserService.get_user_by_email(request.email)
    reset_token = None
    
    if user:
        reset_token = PasswordResetService.generate_reset_token(user.id)
        frontend_url = get_frontend_url()
        
        email_sent = EmailService.send_password_reset_email(
            to_email=user.email,
            reset_token=reset_token,
            frontend_url=frontend_url,
        )
        
        if not email_sent:
            logger.warning(f"Failed to send password reset email to {user.email}")
    
    response_data = {
        "success": True,
        "message": "If the email exists, a password reset link has been sent",
    }
    
    if reset_token:
        response_data["reset_token"] = reset_token
        response_data["reset_url"] = f"{get_frontend_url()}/reset-password?token={reset_token}"
    
    return AuthResponse(**response_data)


@router.get("/password-reset/validate", response_model=TokenValidateResponse)
async def validate_reset_token(token: str):
    is_valid, message, user_id = PasswordResetService.validate_reset_token(token)
    
    return TokenValidateResponse(
        valid=is_valid,
        message=message,
        user_id=user_id if is_valid else None,
    )


@router.post("/password-reset/confirm", response_model=AuthResponse)
async def confirm_password_reset(request: PasswordResetConfirm):
    is_valid, message, user_id = PasswordResetService.validate_reset_token(request.token)
    
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message,
        )
    
    is_valid_password, password_error = PasswordService.validate_password_strength(request.new_password)
    if not is_valid_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=password_error,
        )
    
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid token",
        )
    
    user = UserService.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    try:
        UserService.update_password(user_id, request.new_password)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    
    PasswordResetService.mark_token_as_used(request.token)
    
    return AuthResponse(
        success=True,
        message="Password has been reset successfully",
    )
