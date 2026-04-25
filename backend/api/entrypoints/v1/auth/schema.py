import re
from pydantic import BaseModel, field_validator
from typing import Optional


EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")


def validate_email(email: str) -> bool:
    if not email:
        return False
    return bool(EMAIL_REGEX.match(email))


class LoginRequest(BaseModel):
    email: str
    password: str

    @field_validator("email")
    @classmethod
    def validate_email_field(cls, v):
        if not validate_email(v):
            raise ValueError("Invalid email format")
        return v


class RegisterRequest(BaseModel):
    email: str
    password: str
    confirm_password: str

    @field_validator("email")
    @classmethod
    def validate_email_field(cls, v):
        if not validate_email(v):
            raise ValueError("Invalid email format")
        return v

    @field_validator("confirm_password")
    @classmethod
    def passwords_match(cls, v, info):
        if "password" in info.data and v != info.data["password"]:
            raise ValueError("Passwords do not match")
        return v


class PasswordResetRequest(BaseModel):
    email: str

    @field_validator("email")
    @classmethod
    def validate_email_field(cls, v):
        if not validate_email(v):
            raise ValueError("Invalid email format")
        return v


class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str
    confirm_password: str

    @field_validator("confirm_password")
    @classmethod
    def passwords_match(cls, v, info):
        if "new_password" in info.data and v != info.data["new_password"]:
            raise ValueError("Passwords do not match")
        return v


class UserResponse(BaseModel):
    id: int
    email: str
    is_active: bool


class AuthResponse(BaseModel):
    success: bool
    message: str
    user: Optional[UserResponse] = None
    reset_token: Optional[str] = None
    reset_url: Optional[str] = None


class TokenValidateResponse(BaseModel):
    valid: bool
    message: str
    user_id: Optional[int] = None
