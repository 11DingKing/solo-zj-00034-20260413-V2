import re
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, field_validator


EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
USERNAME_REGEX = re.compile(r"^[a-zA-Z0-9_]{3,20}$")


def validate_email(email: str) -> bool:
    if not email:
        return False
    return bool(EMAIL_REGEX.match(email))


def validate_username(username: str) -> bool:
    if not username:
        return False
    return bool(USERNAME_REGEX.match(username))


class User(BaseModel):
    id: int
    email: str
    username: str
    password_hash: str
    created_at: datetime
    is_active: bool = True

    @field_validator("email")
    @classmethod
    def validate_email_field(cls, v):
        if not validate_email(v):
            raise ValueError("Invalid email format")
        return v

    @field_validator("username")
    @classmethod
    def validate_username_field(cls, v):
        if not validate_username(v):
            raise ValueError("Invalid username format. Must be 3-20 characters, letters, numbers and underscore only.")
        return v


class UserCreate(BaseModel):
    email: str
    username: str
    password: str

    @field_validator("email")
    @classmethod
    def validate_email_field(cls, v):
        if not validate_email(v):
            raise ValueError("Invalid email format")
        return v

    @field_validator("username")
    @classmethod
    def validate_username_field(cls, v):
        if not validate_username(v):
            raise ValueError("Invalid username format. Must be 3-20 characters, letters, numbers and underscore only.")
        return v


class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    created_at: datetime
    is_active: bool


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


class PasswordChange(BaseModel):
    old_password: str
    new_password: str
