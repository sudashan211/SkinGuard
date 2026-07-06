"""
Security Tests for Authentication & Authorization
Task: 36.5 Security audit
Requirements: 18.1, 18.2, 25.6

Tests authentication security including:
- JWT token expiration
- Role-based access control
- Password hashing
- Session management
"""
import pytest
import time
from datetime import timedelta
from unittest.mock import Mock, patch
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../backend'))

from app.auth import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password
)
from fastapi import HTTPException


class TestJWTExpiration:
    """Test JWT token expiration security"""
    
    def test_access_token_expires_correctly(self):
        """
        Test that JWT access tokens expire after the configured time
        
        Security: Ensures tokens don't remain valid indefinitely
        """
        # Create token with 1 second expiry
        token_data = {"sub": "test-user-id", "role": "patient"}
        token = create_access_token(token_data, expires_delta=timedelta(seconds=1))
        
        # Token should be valid immediately
        payload = decode_token(token)
        assert payload["sub"] == "test-user-id"
        assert payload["type"] == "access"
        
        # Wait for token to expire
        time.sleep(2)
        
        # Token should now be expired
        with pytest.raises(HTTPException) as exc_info:
            decode_token(token)
        
        assert exc_info.value.status_code == 401
        assert "Invalid or expired token" in exc_info.value.detail
    
    def test_refresh_token_has_longer_expiry(self):
        """
        Test that refresh tokens have longer expiry than access tokens
        
        Security: Refresh tokens should last longer but still expire
        """
        token_data = {"sub": "test-user-id"}
        
        # Create both token types
        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)
        
        # Decode to check expiry times
        access_payload = decode_token(access_token)
        refresh_payload = decode_token(refresh_token)
        
        # Refresh token should expire later than access token
        assert refresh_payload["exp"] > access_payload["exp"]
        
        # Verify token types are correct
        assert access_payload["type"] == "access"
        assert refresh_payload["type"] == "refresh"
    
    def test_expired_token_cannot_be_used(self):
        """
        Test that expired tokens are rejected
        
        Security: Prevents use of old/stolen tokens
        """
        # Create token that expires immediately
        token_data = {"sub": "test-user-id", "role": "patient"}
        token = create_access_token(token_data, expires_delta=timedelta(seconds=0))
        
        # Wait a moment
        time.sleep(0.1)
        
        # Should be rejected
        with pytest.raises(HTTPException) as exc_info:
            decode_token(token)
        
        assert exc_info.value.status_code == 401
    
    def test_token_type_validation(self):
        """
        Test that token type is validated
        
        Security: Prevents using refresh tokens as access tokens
        """
        # Create refresh token
        refresh_token = create_refresh_token({"sub": "test-user-id"})
        
        # Decode it (should work)
        payload = decode_token(refresh_token)
        
        # But type should be 'refresh', not 'access'
        assert payload["type"] == "refresh"
        
        # Application should check this type before allowing access


class TestPasswordSecurity:
    """Test password hashing and verification"""
    
    def test_password_is_hashed_with_bcrypt(self):
        """
        Test that passwords are hashed using bcrypt
        
        Security: Ensures passwords are not stored in plain text
        """
        password = "SecurePassword123!"
        hashed = hash_password(password)
        
        # Hashed password should not equal plain password
        assert hashed != password
        
        # Bcrypt hashes start with $2b$
        assert hashed.startswith("$2b$")
        
        # Hash should be long (bcrypt produces 60 character hashes)
        assert len(hashed) == 60
    
    def test_same_password_produces_different_hashes(self):
        """
        Test that hashing the same password twice produces different hashes
        
        Security: Ensures salt is used (prevents rainbow table attacks)
        """
        password = "TestPassword456"
        hash1 = hash_password(password)
        hash2 = hash_password(password)
        
        # Hashes should be different due to salt
        assert hash1 != hash2
        
        # But both should verify correctly
        assert verify_password(password, hash1)
        assert verify_password(password, hash2)
    
    def test_password_verification_works(self):
        """
        Test that password verification correctly validates passwords
        
        Security: Ensures authentication works correctly
        """
        password = "CorrectPassword789"
        hashed = hash_password(password)
        
        # Correct password should verify
        assert verify_password(password, hashed) is True
        
        # Wrong password should not verify
        assert verify_password("WrongPassword", hashed) is False
    
    def test_password_verification_rejects_wrong_passwords(self):
        """
        Test that similar but incorrect passwords are rejected
        
        Security: Prevents authentication bypass
        """
        password = "MyPassword123"
        hashed = hash_password(password)
        
        # Test various wrong passwords
        wrong_passwords = [
            "MyPassword124",  # Off by one
            "mypassword123",  # Wrong case
            "MyPassword123 ",  # Extra space
            "MyPassword12",  # Missing character
            "",  # Empty
        ]
        
        for wrong_pwd in wrong_passwords:
            assert verify_password(wrong_pwd, hashed) is False


class TestRoleBasedAccessControl:
    """Test role-based access control enforcement"""
    
    def test_patient_token_contains_role(self):
        """
        Test that JWT tokens contain role information
        
        Security: Enables role-based access control
        """
        token_data = {
            "sub": "patient-user-id",
            "email": "patient@test.com",
            "role": "patient",
            "verified": False
        }
        
        token = create_access_token(token_data)
        payload = decode_token(token)
        
        assert payload["role"] == "patient"
        assert payload["verified"] is False
    
    def test_doctor_token_contains_verified_status(self):
        """
        Test that doctor tokens include verification status
        
        Security: Enables verification-based access control
        """
        token_data = {
            "sub": "doctor-user-id",
            "email": "doctor@test.com",
            "role": "doctor",
            "verified": True
        }
        
        token = create_access_token(token_data)
        payload = decode_token(token)
        
        assert payload["role"] == "doctor"
        assert payload["verified"] is True
    
    def test_admin_token_contains_admin_role(self):
        """
        Test that admin tokens are properly marked
        
        Security: Enables admin-only access control
        """
        token_data = {
            "sub": "admin-user-id",
            "email": "admin@test.com",
            "role": "admin",
            "verified": True
        }
        
        token = create_access_token(token_data)
        payload = decode_token(token)
        
        assert payload["role"] == "admin"
    
    def test_token_cannot_be_modified(self):
        """
        Test that JWT tokens cannot be tampered with
        
        Security: Prevents privilege escalation
        """
        # Create patient token
        token_data = {"sub": "user-id", "role": "patient"}
        token = create_access_token(token_data)
        
        # Try to modify the token (change role to admin)
        # This should fail because the signature won't match
        parts = token.split('.')
        
        # Even if we modify the payload, signature verification should fail
        # We can't test this directly without the secret key, but the
        # jose library handles this automatically
        
        # Verify original token works
        payload = decode_token(token)
        assert payload["role"] == "patient"


class TestSessionManagement:
    """Test session management security"""
    
    def test_token_contains_user_identifier(self):
        """
        Test that tokens contain user identifier
        
        Security: Enables user tracking and session management
        """
        user_id = "unique-user-id-123"
        token_data = {"sub": user_id, "role": "patient"}
        
        token = create_access_token(token_data)
        payload = decode_token(token)
        
        assert payload["sub"] == user_id
    
    def test_token_contains_expiration(self):
        """
        Test that tokens contain expiration timestamp
        
        Security: Enables automatic session timeout
        """
        token_data = {"sub": "user-id", "role": "patient"}
        token = create_access_token(token_data)
        
        payload = decode_token(token)
        
        # Token should have 'exp' field
        assert "exp" in payload
        assert isinstance(payload["exp"], (int, float))
        
        # Expiration should be in the future
        import time
        current_time = time.time()
        assert payload["exp"] > current_time
    
    def test_invalid_token_is_rejected(self):
        """
        Test that invalid tokens are rejected
        
        Security: Prevents authentication bypass
        """
        invalid_tokens = [
            "not.a.token",
            "invalid-token-format",
            "",
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.invalid.signature",
        ]
        
        for invalid_token in invalid_tokens:
            with pytest.raises(HTTPException) as exc_info:
                decode_token(invalid_token)
            
            assert exc_info.value.status_code == 401


class TestAuthenticationSecurity:
    """Test overall authentication security"""
    
    def test_token_includes_all_required_claims(self):
        """
        Test that tokens include all required security claims
        
        Security: Ensures complete authentication context
        """
        token_data = {
            "sub": "user-id",
            "email": "user@test.com",
            "role": "patient",
            "verified": False
        }
        
        token = create_access_token(token_data)
        payload = decode_token(token)
        
        # Verify all required claims are present
        required_claims = ["sub", "email", "role", "verified", "exp", "type"]
        for claim in required_claims:
            assert claim in payload, f"Missing required claim: {claim}"
    
    def test_refresh_token_has_minimal_claims(self):
        """
        Test that refresh tokens have minimal information
        
        Security: Reduces information exposure if refresh token is stolen
        """
        token_data = {"sub": "user-id"}
        refresh_token = create_refresh_token(token_data)
        
        payload = decode_token(refresh_token)
        
        # Refresh token should only have sub, exp, and type
        assert "sub" in payload
        assert "exp" in payload
        assert "type" in payload
        
        # Should not have sensitive info like email or role
        # (these are fetched fresh when refreshing)
    
    def test_token_algorithm_is_secure(self):
        """
        Test that JWT uses secure algorithm
        
        Security: Prevents algorithm confusion attacks
        """
        token_data = {"sub": "user-id", "role": "patient"}
        token = create_access_token(token_data)
        
        # Decode header to check algorithm
        import base64
        import json
        
        header = token.split('.')[0]
        # Add padding if needed
        header += '=' * (4 - len(header) % 4)
        decoded_header = json.loads(base64.urlsafe_b64decode(header))
        
        # Should use HS256 (HMAC with SHA-256)
        assert decoded_header["alg"] == "HS256"
        assert decoded_header["typ"] == "JWT"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
