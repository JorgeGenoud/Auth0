"""
Unit tests for JWT authentication module.
"""
import pytest
from datetime import timedelta
from fastapi import HTTPException
from auth.jwt_auth import create_access_token, verify_token, get_current_user
from config import settings


class TestCreateAccessToken:
    """Tests for create_access_token function."""
    
    def test_create_access_token_with_default_expiration(self):
        """Test creating a token with default expiration."""
        data = {"sub": "testuser"}
        token = create_access_token(data)
        
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_create_access_token_with_custom_expiration(self):
        """Test creating a token with custom expiration."""
        data = {"sub": "testuser"}
        expires_delta = timedelta(minutes=60)
        token = create_access_token(data, expires_delta=expires_delta)
        
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_create_access_token_includes_iat_and_exp(self):
        """Test that token includes issued at and expiration claims."""
        data = {"sub": "testuser"}
        token = create_access_token(data)
        
        # Decode token to verify claims
        import jwt
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm]
        )
        
        assert "iat" in payload
        assert "exp" in payload
        assert payload["sub"] == "testuser"


class TestVerifyToken:
    """Tests for verify_token function."""
    
    def test_verify_valid_token(self):
        """Test verifying a valid token."""
        # Create a valid token
        token = create_access_token({"sub": "testuser"})
        
        # Mock HTTPBearer credentials
        from fastapi.security import HTTPAuthorizationCredentials
        from unittest.mock import Mock
        
        credentials = Mock(spec=HTTPAuthorizationCredentials)
        credentials.credentials = token
        
        # Verify token
        payload = verify_token(credentials)
        
        assert payload["sub"] == "testuser"
        assert "iat" in payload
        assert "exp" in payload
    
    def test_verify_expired_token(self):
        """Test verifying an expired token raises exception."""
        # Create an expired token
        from datetime import datetime, timedelta
        import jwt
        
        data = {"sub": "testuser", "exp": datetime.utcnow() - timedelta(hours=1)}
        expired_token = jwt.encode(
            data,
            settings.jwt_secret_key,
            algorithm=settings.jwt_algorithm
        )
        
        # Mock HTTPBearer credentials
        from fastapi.security import HTTPAuthorizationCredentials
        from unittest.mock import Mock
        
        credentials = Mock(spec=HTTPAuthorizationCredentials)
        credentials.credentials = expired_token
        
        # Verify that expired token raises exception
        with pytest.raises(HTTPException) as exc_info:
            verify_token(credentials)
        
        assert exc_info.value.status_code == 401
        assert "expired" in exc_info.value.detail.lower()
    
    def test_verify_invalid_token(self):
        """Test verifying an invalid token raises exception."""
        # Mock HTTPBearer credentials with invalid token
        from fastapi.security import HTTPAuthorizationCredentials
        from unittest.mock import Mock
        
        credentials = Mock(spec=HTTPAuthorizationCredentials)
        credentials.credentials = "invalid-token-string"
        
        # Verify that invalid token raises exception
        with pytest.raises(HTTPException) as exc_info:
            verify_token(credentials)
        
        assert exc_info.value.status_code == 401


class TestGetCurrentUser:
    """Tests for get_current_user function."""
    
    def test_get_current_user_with_valid_token(self):
        """Test getting current user from valid token."""
        token_data = {
            "sub": "testuser",
            "email": "test@example.com",
            "iat": 1234567890,
            "exp": 9999999999
        }
        
        user = get_current_user(token_data)
        
        assert user["sub"] == "testuser"
        assert user["email"] == "test@example.com"
