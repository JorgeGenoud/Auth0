"""
Unit tests for configuration module.
"""
import pytest
import os
from unittest.mock import patch
from pydantic import ValidationError


class TestSettings:
    """Tests for Settings class."""
    
    def test_settings_loads_from_env(self):
        """Test that settings can be loaded from environment variables."""
        with patch.dict(os.environ, {
            "JWT_SECRET_KEY": "test-secret",
            "AUTH0_DOMAIN": "test.auth0.com",
            "AUTH0_API_AUDIENCE": "https://test.auth0.com/api/v2/"
        }):
            from config import Settings
            
            settings = Settings()
            
            assert settings.jwt_secret_key == "test-secret"
            assert settings.auth0_domain == "test.auth0.com"
    
    def test_settings_has_default_values(self):
        """Test that settings have default values."""
        with patch.dict(os.environ, {
            "JWT_SECRET_KEY": "test-secret"
        }, clear=False):
            from config import Settings
            
            settings = Settings()
            
            assert settings.jwt_algorithm == "RS256"
            assert settings.jwt_access_token_expire_minutes == 30
            assert settings.auth_provider == "auth0"
    
    def test_settings_requires_jwt_secret_key(self):
        """Test that JWT secret key is required."""
        with patch.dict(os.environ, {}, clear=True):
            from config import Settings
            
            with pytest.raises(ValidationError):
                Settings()
    
    def test_settings_optional_fields(self):
        """Test that optional fields can be None."""
        with patch.dict(os.environ, {
            "JWT_SECRET_KEY": "test-secret",
            "AUTH0_MANAGEMENT_TOKEN": "",
            "AUTH0_CLIENT_ID": "",
            "AUTH0_CLIENT_SECRET": ""
        }):
            from config import Settings
            
            settings = Settings()
            
            # These should be None or empty string
            assert settings.auth0_management_token in [None, ""]
            assert settings.auth0_client_id in [None, ""]
