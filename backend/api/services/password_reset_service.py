import hmac
import hashlib
import time
import os
import base64
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
from dataclasses import dataclass

from api.services.user_service import UserService


@dataclass
class ResetTokenData:
    user_id: int
    expires_at: float
    used: bool = False


class PasswordResetService:
    RESET_TOKEN_EXPIRY_MINUTES = 15
    _used_tokens: Dict[str, ResetTokenData] = {}
    _secret_key: bytes = None

    @classmethod
    def _get_secret_key(cls) -> bytes:
        if cls._secret_key is None:
            env_secret = os.getenv("SECRET_KEY", "")
            if not env_secret:
                env_secret = "dev-secret-key-change-in-production"
            cls._secret_key = env_secret.encode("utf-8")
        return cls._secret_key

    @classmethod
    def _generate_signature(cls, user_id: int, timestamp: float) -> str:
        secret = cls._get_secret_key()
        message = f"{user_id}:{timestamp}".encode("utf-8")
        signature = hmac.new(secret, message, hashlib.sha256).digest()
        return base64.urlsafe_b64encode(signature).decode("utf-8").rstrip("=")

    @classmethod
    def _verify_signature(cls, user_id: int, timestamp: float, signature: str) -> bool:
        expected_signature = cls._generate_signature(user_id, timestamp)
        return hmac.compare_digest(expected_signature, signature)

    @classmethod
    def generate_reset_token(cls, user_id: int) -> str:
        expires_at = time.time() + (cls.RESET_TOKEN_EXPIRY_MINUTES * 60)
        signature = cls._generate_signature(user_id, expires_at)
        
        token_data = f"{user_id}:{expires_at}:{signature}"
        token = base64.urlsafe_b64encode(token_data.encode("utf-8")).decode("utf-8").rstrip("=")
        
        cls._used_tokens[token] = ResetTokenData(
            user_id=user_id,
            expires_at=expires_at,
            used=False,
        )
        
        return token

    @classmethod
    def _parse_token(cls, token: str) -> Optional[Tuple[int, float, str]]:
        try:
            padded_token = token + "=" * (4 - len(token) % 4)
            decoded = base64.urlsafe_b64decode(padded_token).decode("utf-8")
            parts = decoded.split(":")
            if len(parts) != 3:
                return None
            user_id = int(parts[0])
            expires_at = float(parts[1])
            signature = parts[2]
            return (user_id, expires_at, signature)
        except Exception:
            return None

    @classmethod
    def validate_reset_token(cls, token: str) -> Tuple[bool, str, Optional[int]]:
        parsed = cls._parse_token(token)
        if not parsed:
            return False, "Invalid token format", None
        
        user_id, expires_at, signature = parsed
        
        if not cls._verify_signature(user_id, expires_at, signature):
            return False, "Invalid token signature", None
        
        if time.time() > expires_at:
            return False, "Token has expired", None
        
        token_data = cls._used_tokens.get(token)
        if not token_data:
            return False, "Token not found or already used", None
        
        if token_data.used:
            return False, "Token has already been used", None
        
        return True, "", user_id

    @classmethod
    def mark_token_as_used(cls, token: str) -> bool:
        token_data = cls._used_tokens.get(token)
        if token_data and not token_data.used:
            token_data.used = True
            return True
        return False

    @classmethod
    def cleanup_expired_tokens(cls):
        current_time = time.time()
        expired_tokens = [
            token for token, data in cls._used_tokens.items()
            if current_time > data.expires_at
        ]
        for token in expired_tokens:
            del cls._used_tokens[token]

    @classmethod
    def get_token_info(cls, token: str) -> Optional[dict]:
        token_data = cls._used_tokens.get(token)
        if not token_data:
            return None
        return {
            "user_id": token_data.user_id,
            "expires_at": datetime.fromtimestamp(token_data.expires_at),
            "used": token_data.used,
            "expires_in_seconds": max(0, int(token_data.expires_at - time.time())),
        }
