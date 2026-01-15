"""
Pytest configuration and fixtures.
"""
import os
import sys
import pytest
from unittest.mock import Mock, patch

# Set environment variables before importing app modules
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key-for-testing-only")
os.environ.setdefault("AUTH0_DOMAIN", "test-domain.auth0.com")
os.environ.setdefault("AUTH0_API_AUDIENCE", "https://test-domain.auth0.com/api/v2/")

from fastapi.testclient import TestClient
from main import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI application."""
    return TestClient(app)


@pytest.fixture(autouse=True)
def mock_settings():
    """Mock settings for testing by modifying the global instance."""
    from config import settings
    
    # Store original values
    original_values = {
        "jwt_secret_key": settings.jwt_secret_key,
        "jwt_algorithm": settings.jwt_algorithm,
        "jwt_access_token_expire_minutes": settings.jwt_access_token_expire_minutes,
        "auth0_domain": settings.auth0_domain,
        "auth0_api_audience": settings.auth0_api_audience,
        "auth0_management_token": settings.auth0_management_token,
        "auth0_client_id": settings.auth0_client_id,
        "auth0_client_secret": settings.auth0_client_secret,
        "auth_provider": settings.auth_provider,
        "api_title": settings.api_title,
        "api_version": settings.api_version,
        "debug": settings.debug
    }
    
    # Set test values
    settings.jwt_secret_key = "test-secret-key-for-testing-only"
    settings.jwt_algorithm = "HS256"
    settings.jwt_access_token_expire_minutes = 30
    settings.auth0_domain = "test-domain.auth0.com"
    settings.auth0_api_audience = "https://test-domain.auth0.com/api/v2/"
    settings.auth0_management_token = "test-management-token"
    settings.auth0_client_id = "test-client-id"
    settings.auth0_client_secret = "test-client-secret"
    settings.auth_provider = "auth0"
    settings.api_title = "Test API"
    settings.api_version = "v1"
    settings.debug = True
    
    yield settings
    
    # Restore original values
    for key, value in original_values.items():
        setattr(settings, key, value)


@pytest.fixture
def mock_auth0_provider():
    """Mock Auth0Provider for testing."""
    from unittest.mock import Mock
    mock_provider = Mock()
    mock_provider.get_token.return_value = "mock-token"
    mock_provider.authenticate_user.return_value = {
        "access_token": "mock-access-token",
        "token_type": "bearer",
        "expires_in": 86400
    }
    mock_provider.get_users.return_value = {
        "users": [
            {
                "user_id": "auth0|123",
                "email": "test@example.com",
                "name": "Test User"
            }
        ],
        "total": 1
    }
    mock_provider.get_user.return_value = {
        "user_id": "auth0|123",
        "email": "test@example.com",
        "name": "Test User"
    }
    mock_provider.create_user.return_value = {
        "user_id": "auth0|456",
        "email": "new@example.com",
        "name": "New User"
    }
    mock_provider.update_user.return_value = {
        "user_id": "auth0|123",
        "email": "updated@example.com",
        "name": "Updated User"
    }
    mock_provider.delete_user.return_value = True
    mock_provider.get_clients.return_value = {
        "clients": [
            {
                "client_id": "test-client-123",
                "name": "Test Client"
            }
        ],
        "total": 1
    }
    mock_provider.health_check.return_value = True
    return mock_provider


@pytest.fixture
def jwt_token():
    """Create a test JWT token."""
    from auth.jwt_auth import create_access_token
    return create_access_token(data={"sub": "testuser"})


@pytest.fixture
def auth_headers(jwt_token):
    """Create authorization headers with JWT token."""
    return {"Authorization": f"Bearer {jwt_token}"}
