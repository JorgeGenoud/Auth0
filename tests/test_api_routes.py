"""
Unit tests for API routes.
"""
import pytest
from unittest.mock import patch, Mock
from fastapi.testclient import TestClient
from main import app


@pytest.fixture
def client():
    """Create a test client."""
    return TestClient(app)


@pytest.fixture
def jwt_token():
    """Create a test JWT token."""
    from auth.jwt_auth import create_access_token
    return create_access_token(data={"sub": "testuser"})


class TestHealthCheck:
    """Tests for health check endpoint."""
    
    def test_health_check_endpoint(self, client, mock_auth0_provider):
        """Test health check endpoint returns status."""
        with patch("api.v1.routes.auth_provider", mock_auth0_provider):
            response = client.get("/api/v1/health")
        
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "api" in data
        assert "auth_provider" in data


class TestAuthEndpoints:
    """Tests for authentication endpoints."""
    
    def test_login_endpoint(self, client, mock_auth0_provider):
        """Test login endpoint generates token."""
        with patch("api.v1.routes.auth_provider", mock_auth0_provider):
            response = client.post(
                "/api/v1/auth/login",
                json={"username": "testuser", "password": "testpass"}
            )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert len(data["access_token"]) > 0


class TestUserEndpoints:
    """Tests for user management endpoints."""
    
    def test_get_users_requires_authentication(self, client):
        """Test that getting users requires JWT authentication."""
        response = client.get("/api/v1/users")
        
        assert response.status_code == 403
    
    def test_get_users_with_valid_token(
        self, client, jwt_token, mock_auth0_provider
    ):
        """Test getting users with valid JWT token."""
        with patch("api.v1.routes.auth_provider", mock_auth0_provider):
            headers = {"Authorization": f"Bearer {jwt_token}"}
            response = client.get("/api/v1/users", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "users" in data
    
    def test_get_users_with_pagination(
        self, client, jwt_token, mock_auth0_provider
    ):
        """Test getting users with pagination parameters."""
        with patch("api.v1.routes.auth_provider", mock_auth0_provider):
            headers = {"Authorization": f"Bearer {jwt_token}"}
            response = client.get(
                "/api/v1/users",
                headers=headers,
                params={"page": 0, "per_page": 10, "include_totals": True}
            )
        
        assert response.status_code == 200
    
    def test_get_user_by_id_requires_authentication(self, client):
        """Test that getting a user requires JWT authentication."""
        response = client.get("/api/v1/users/auth0|123")
        
        assert response.status_code == 403
    
    def test_get_user_by_id_with_valid_token(
        self, client, jwt_token, mock_auth0_provider
    ):
        """Test getting a specific user with valid token."""
        with patch("api.v1.routes.auth_provider", mock_auth0_provider):
            headers = {"Authorization": f"Bearer {jwt_token}"}
            response = client.get("/api/v1/users/auth0|123", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == "auth0|123"
    
    def test_get_user_not_found(
        self, client, jwt_token, mock_auth0_provider
    ):
        """Test getting a non-existent user returns 404."""
        mock_auth0_provider.get_user.return_value = None
        
        with patch("api.v1.routes.auth_provider", mock_auth0_provider):
            headers = {"Authorization": f"Bearer {jwt_token}"}
            response = client.get("/api/v1/users/invalid-id", headers=headers)
        
        assert response.status_code == 404
    
    def test_create_user_requires_authentication(self, client):
        """Test that creating a user requires JWT authentication."""
        user_data = {
            "email": "new@example.com",
            "password": "SecurePass123!",
            "connection": "Username-Password-Authentication"
        }
        response = client.post("/api/v1/users", json=user_data)
        
        assert response.status_code == 403
    
    def test_create_user_with_valid_token(
        self, client, jwt_token, mock_auth0_provider
    ):
        """Test creating a user with valid token."""
        user_data = {
            "email": "new@example.com",
            "password": "SecurePass123!",
            "connection": "Username-Password-Authentication"
        }
        
        with patch("api.v1.routes.auth_provider", mock_auth0_provider):
            headers = {"Authorization": f"Bearer {jwt_token}"}
            response = client.post(
                "/api/v1/users",
                json=user_data,
                headers=headers
            )
        
        assert response.status_code == 201
        data = response.json()
        assert "user_id" in data
    
    def test_create_user_validation_error(
        self, client, jwt_token, mock_auth0_provider
    ):
        """Test creating user with invalid data returns 422."""
        invalid_data = {"email": "invalid-email"}  # Missing required fields
        
        with patch("api.v1.routes.auth_provider", mock_auth0_provider):
            headers = {"Authorization": f"Bearer {jwt_token}"}
            response = client.post(
                "/api/v1/users",
                json=invalid_data,
                headers=headers
            )
        
        assert response.status_code == 422
    
    def test_update_user_requires_authentication(self, client):
        """Test that updating a user requires JWT authentication."""
        user_data = {"email": "updated@example.com"}
        response = client.patch("/api/v1/users/auth0|123", json=user_data)
        
        assert response.status_code == 403
    
    def test_update_user_with_valid_token(
        self, client, jwt_token, mock_auth0_provider
    ):
        """Test updating a user with valid token."""
        user_data = {"email": "updated@example.com"}
        
        with patch("api.v1.routes.auth_provider", mock_auth0_provider):
            headers = {"Authorization": f"Bearer {jwt_token}"}
            response = client.patch(
                "/api/v1/users/auth0|123",
                json=user_data,
                headers=headers
            )
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "updated@example.com"
    
    def test_update_user_with_empty_data(
        self, client, jwt_token, mock_auth0_provider
    ):
        """Test updating user with empty data returns 400."""
        with patch("api.v1.routes.auth_provider", mock_auth0_provider):
            headers = {"Authorization": f"Bearer {jwt_token}"}
            response = client.patch(
                "/api/v1/users/auth0|123",
                json={},
                headers=headers
            )
        
        assert response.status_code == 400
    
    def test_delete_user_requires_authentication(self, client):
        """Test that deleting a user requires JWT authentication."""
        response = client.delete("/api/v1/users/auth0|123")
        
        assert response.status_code == 403
    
    def test_delete_user_with_valid_token(
        self, client, jwt_token, mock_auth0_provider
    ):
        """Test deleting a user with valid token."""
        with patch("api.v1.routes.auth_provider", mock_auth0_provider):
            headers = {"Authorization": f"Bearer {jwt_token}"}
            response = client.delete("/api/v1/users/auth0|123", headers=headers)
        
        assert response.status_code == 204
    
    def test_delete_user_not_found(
        self, client, jwt_token, mock_auth0_provider
    ):
        """Test deleting non-existent user returns 404."""
        mock_auth0_provider.delete_user.return_value = False
        
        with patch("api.v1.routes.auth_provider", mock_auth0_provider):
            headers = {"Authorization": f"Bearer {jwt_token}"}
            response = client.delete("/api/v1/users/invalid-id", headers=headers)
        
        assert response.status_code == 404


class TestClientEndpoints:
    """Tests for client management endpoints."""
    
    def test_get_clients_requires_authentication(self, client):
        """Test that getting clients requires JWT authentication."""
        response = client.get("/api/v1/clients")
        
        assert response.status_code == 403
    
    def test_get_clients_with_valid_token(
        self, client, jwt_token, mock_auth0_provider
    ):
        """Test getting clients with valid token."""
        with patch("api.v1.routes.auth_provider", mock_auth0_provider):
            headers = {"Authorization": f"Bearer {jwt_token}"}
            response = client.get("/api/v1/clients", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "clients" in data


class TestRootEndpoints:
    """Tests for root endpoints."""
    
    def test_root_endpoint(self, client):
        """Test root endpoint returns API information."""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
    
    def test_api_info_endpoint(self, client):
        """Test API info endpoint."""
        response = client.get("/api/v1")
        
        assert response.status_code == 200
        data = response.json()
        assert "api_version" in data
        assert "endpoints" in data
