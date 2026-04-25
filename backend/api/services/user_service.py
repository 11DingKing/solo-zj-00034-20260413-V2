import hashlib
import os
from datetime import datetime
from typing import Dict, Optional

from api.models.user import User, UserCreate, UserResponse


class PasswordService:
    @staticmethod
    def hash_password(password: str) -> str:
        salt = os.urandom(32)
        key = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100000)
        return salt.hex() + ":" + key.hex()

    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        salt_hex, key_hex = password_hash.split(":")
        salt = bytes.fromhex(salt_hex)
        key = bytes.fromhex(key_hex)
        new_key = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100000)
        return new_key == key

    @staticmethod
    def validate_password_strength(password: str) -> tuple[bool, str]:
        if len(password) < 8:
            return False, "Password must be at least 8 characters long"
        if not any(c.isdigit() for c in password):
            return False, "Password must contain at least one digit"
        if not any(c.isalpha() for c in password):
            return False, "Password must contain at least one letter"
        return True, ""


class UserService:
    _users: Dict[int, User] = {}
    _email_to_id: Dict[str, int] = {}
    _next_id: int = 1

    @classmethod
    def create_user(cls, user_create: UserCreate) -> UserResponse:
        if user_create.email in cls._email_to_id:
            raise ValueError("User with this email already exists")

        is_valid, error_msg = PasswordService.validate_password_strength(user_create.password)
        if not is_valid:
            raise ValueError(error_msg)

        password_hash = PasswordService.hash_password(user_create.password)
        user = User(
            id=cls._next_id,
            email=user_create.email,
            password_hash=password_hash,
            created_at=datetime.now(),
            is_active=True,
        )

        cls._users[user.id] = user
        cls._email_to_id[user.email] = user.id
        cls._next_id += 1

        return UserResponse(
            id=user.id,
            email=user.email,
            created_at=user.created_at,
            is_active=user.is_active,
        )

    @classmethod
    def get_user_by_id(cls, user_id: int) -> Optional[User]:
        return cls._users.get(user_id)

    @classmethod
    def get_user_by_email(cls, email: str) -> Optional[User]:
        user_id = cls._email_to_id.get(email)
        if user_id:
            return cls._users.get(user_id)
        return None

    @classmethod
    def update_password(cls, user_id: int, new_password: str) -> bool:
        user = cls._users.get(user_id)
        if not user:
            return False

        is_valid, error_msg = PasswordService.validate_password_strength(new_password)
        if not is_valid:
            raise ValueError(error_msg)

        user.password_hash = PasswordService.hash_password(new_password)
        return True

    @classmethod
    def authenticate_user(cls, email: str, password: str) -> Optional[UserResponse]:
        user = cls.get_user_by_email(email)
        if not user:
            return None
        if not PasswordService.verify_password(password, user.password_hash):
            return None
        return UserResponse(
            id=user.id,
            email=user.email,
            created_at=user.created_at,
            is_active=user.is_active,
        )

    @classmethod
    def clear_all_users(cls):
        cls._users.clear()
        cls._email_to_id.clear()
        cls._next_id = 1
