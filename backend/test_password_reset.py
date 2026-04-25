#!/usr/bin/env python3
"""
Test script for password reset functionality.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from api.models.user import UserCreate
from api.services.user_service import UserService, PasswordService
from api.services.password_reset_service import PasswordResetService


def test_password_strength_validation():
    print("\n=== Testing Password Strength Validation ===")
    
    test_cases = [
        ("short", False, "too short"),
        ("1234567", False, "7 chars"),
        ("12345678", False, "only numbers"),
        ("abcdefgh", False, "only letters"),
        ("password123", True, "valid password"),
        ("MyP@ssw0rd", True, "strong password"),
    ]
    
    for password, expected_valid, description in test_cases:
        is_valid, message = PasswordService.validate_password_strength(password)
        status = "✓" if is_valid == expected_valid else "✗"
        print(f"{status} {description}: '{password}' -> valid={is_valid}")
        if is_valid != expected_valid:
            print(f"  Expected: valid={expected_valid}, Got: valid={is_valid}")
    
    print("Password strength validation tests completed.")


def test_user_creation_and_authentication():
    print("\n=== Testing User Creation and Authentication ===")
    
    UserService.clear_all_users()
    
    user_create = UserCreate(email="test@example.com", password="TestPass123")
    user = UserService.create_user(user_create)
    print(f"✓ Created user: {user.email} (id={user.id})")
    
    auth_user = UserService.authenticate_user("test@example.com", "TestPass123")
    assert auth_user is not None, "Authentication should succeed with correct password"
    print(f"✓ Authentication successful with correct password")
    
    auth_user = UserService.authenticate_user("test@example.com", "wrongpassword")
    assert auth_user is None, "Authentication should fail with wrong password"
    print(f"✓ Authentication failed with wrong password (expected)")
    
    print("User creation and authentication tests completed.")


def test_password_reset_token():
    print("\n=== Testing Password Reset Token ===")
    
    UserService.clear_all_users()
    
    user_create = UserCreate(email="reset@example.com", password="OldPass123")
    user = UserService.create_user(user_create)
    
    token = PasswordResetService.generate_reset_token(user.id)
    print(f"✓ Generated reset token for user {user.id}")
    print(f"  Token: {token[:30]}...")
    
    is_valid, message, user_id = PasswordResetService.validate_reset_token(token)
    assert is_valid, f"Token should be valid: {message}"
    assert user_id == user.id, f"User ID should match: {user_id} != {user.id}"
    print(f"✓ Token validation passed: user_id={user_id}")
    
    token_info = PasswordResetService.get_token_info(token)
    assert token_info is not None, "Token info should exist"
    print(f"✓ Token info: expires_in={token_info['expires_in_seconds']}s, used={token_info['used']}")
    
    marked = PasswordResetService.mark_token_as_used(token)
    assert marked, "Should mark token as used"
    print(f"✓ Marked token as used")
    
    is_valid, message, user_id = PasswordResetService.validate_reset_token(token)
    assert not is_valid, "Token should be invalid after being used"
    print(f"✓ Token validation failed after use (expected): {message}")
    
    print("Password reset token tests completed.")


def test_invalid_tokens():
    print("\n=== Testing Invalid Tokens ===")
    
    invalid_token = "invalidtoken123"
    is_valid, message, user_id = PasswordResetService.validate_reset_token(invalid_token)
    assert not is_valid, "Invalid token should fail validation"
    print(f"✓ Invalid token rejected: {message}")
    
    import time
    from api.services.password_reset_service import PasswordResetService as PRS
    
    original_expiry = PRS.RESET_TOKEN_EXPIRY_MINUTES
    PRS.RESET_TOKEN_EXPIRY_MINUTES = -1
    
    UserService.clear_all_users()
    user_create = UserCreate(email="expired@example.com", password="TestPass123")
    user = UserService.create_user(user_create)
    
    expired_token = PRS.generate_reset_token(user.id)
    is_valid, message, user_id = PRS.validate_reset_token(expired_token)
    assert not is_valid, "Expired token should fail validation"
    print(f"✓ Expired token rejected: {message}")
    
    PRS.RESET_TOKEN_EXPIRY_MINUTES = original_expiry
    
    print("Invalid token tests completed.")


def test_password_update():
    print("\n=== Testing Password Update ===")
    
    UserService.clear_all_users()
    
    user_create = UserCreate(email="update@example.com", password="OldPass123")
    user = UserService.create_user(user_create)
    
    auth_user = UserService.authenticate_user("update@example.com", "OldPass123")
    assert auth_user is not None, "Should authenticate with old password"
    print(f"✓ Authenticated with old password")
    
    updated = UserService.update_password(user.id, "NewPass456")
    assert updated, "Should update password"
    print(f"✓ Password updated")
    
    auth_user = UserService.authenticate_user("update@example.com", "OldPass123")
    assert auth_user is None, "Should not authenticate with old password"
    print(f"✓ Old password no longer works (expected)")
    
    auth_user = UserService.authenticate_user("update@example.com", "NewPass456")
    assert auth_user is not None, "Should authenticate with new password"
    print(f"✓ Authenticated with new password")
    
    print("Password update tests completed.")


def main():
    print("=" * 60)
    print("Password Reset Functionality Tests")
    print("=" * 60)
    
    try:
        test_password_strength_validation()
        test_user_creation_and_authentication()
        test_password_reset_token()
        test_invalid_tokens()
        test_password_update()
        
        print("\n" + "=" * 60)
        print("All tests passed! ✓")
        print("=" * 60)
        return 0
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        return 1
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
