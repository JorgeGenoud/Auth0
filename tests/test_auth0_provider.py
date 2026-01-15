"""
Unit tests for Auth0 provider implementation.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from auth.providers.auth0 import Auth0Provider


class TestAuth0Provider:
    """Tests for Auth0Provider class."""
    
    @pytest.fixture
    def provider(self, mock_settings):
        """Create an Auth0Provider instance for testing."""
        return Auth0Provider()
    
    def test_initialization(self, provider):
        """Test Auth0Provider initialization."""
        from config import settings
        assert provider.domain == settings.auth0_domain
        assert provider.api_audience == settings.auth0_api_audience
        # Verify provider is properly initialized with base_url
        assert provider.base_url == f"https://{provider.domain}/api/v2"
        # Verify all attributes are initialized (may be None)
        assert hasattr(provider, 'management_token')
        assert hasattr(provider, 'client_id')
        assert hasattr(provider, 'client_secret')
    
    def test_get_token_with_management_token(self, provider):
        """Test getting token when management token is configured."""
        provider.management_token = "test-token"
        token = provider.get_token()
        
        assert token == "test-token"
    
    @patch("auth.providers.auth0.httpx.Client")
    def test_get_token_with_client_credentials(self, mock_client_class, provider):
        """Test getting token using client credentials."""
        provider.management_token = None
        provider.client_id = "test-client-id"
        provider.client_secret = "test-client-secret"
        
        # Mock HTTP response
        mock_response = Mock()
        mock_response.json.return_value = {"access_token": "new-token"}
        mock_response.raise_for_status = Mock()
        
        mock_client = Mock()
        mock_client.post.return_value = mock_response
        mock_client_class.return_value.__enter__.return_value = mock_client
        
        token = provider.get_token()
        
        assert token == "new-token"
        mock_client.post.assert_called_once()
    
    def test_get_token_returns_none_when_no_credentials(self, provider):
        """Test get_token returns None when no credentials available."""
        provider.management_token = None
        provider.client_id = None
        provider.client_secret = None
        
        token = provider.get_token()
        
        assert token is None
    
    def test_get_headers_with_valid_token(self, provider):
        """Test getting headers with valid token."""
        provider.get_token = Mock(return_value="test-token")
        
        headers = provider._get_headers()
        
        assert headers["Authorization"] == "Bearer test-token"
        assert headers["Content-Type"] == "application/json"
    
    def test_get_headers_raises_when_no_token(self, provider):
        """Test _get_headers raises error when token unavailable."""
        provider.get_token = Mock(return_value=None)
        
        with pytest.raises(ValueError, match="Unable to obtain authentication token"):
            provider._get_headers()
    
    @patch("auth.providers.auth0.httpx.Client")
    def test_get_users_success(self, mock_client_class, provider):
        """Test getting users successfully."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "users": [{"user_id": "123", "email": "test@example.com"}],
            "total": 1
        }
        mock_response.raise_for_status = Mock()
        
        mock_client = Mock()
        mock_client.get.return_value = mock_response
        mock_client_class.return_value.__enter__.return_value = mock_client
        
        provider.get_token = Mock(return_value="test-token")
        
        result = provider.get_users(page=0, per_page=50, include_totals=True)
        
        assert "users" in result
        assert len(result["users"]) == 1
        assert result["total"] == 1
    
    @patch("auth.providers.auth0.httpx.Client")
    def test_get_users_handles_error(self, mock_client_class, provider):
        """Test get_users handles HTTP errors gracefully."""
        import httpx
        
        mock_client = Mock()
        mock_client.get.side_effect = httpx.HTTPError("Connection error")
        mock_client_class.return_value.__enter__.return_value = mock_client
        
        provider.get_token = Mock(return_value="test-token")
        
        result = provider.get_users()
        
        assert "error" in result
        assert result["users"] == []
        assert result["total"] == 0
    
    @patch("auth.providers.auth0.httpx.Client")
    def test_get_user_success(self, mock_client_class, provider):
        """Test getting a specific user successfully."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "user_id": "auth0|123",
            "email": "test@example.com"
        }
        mock_response.raise_for_status = Mock()
        
        mock_client = Mock()
        mock_client.get.return_value = mock_response
        mock_client_class.return_value.__enter__.return_value = mock_client
        
        provider.get_token = Mock(return_value="test-token")
        
        user = provider.get_user("auth0|123")
        
        assert user is not None
        assert user["user_id"] == "auth0|123"
        assert user["email"] == "test@example.com"
    
    @patch("auth.providers.auth0.httpx.Client")
    def test_get_user_returns_none_on_error(self, mock_client_class, provider):
        """Test get_user returns None on error."""
        import httpx
        
        mock_client = Mock()
        mock_client.get.side_effect = httpx.HTTPError("Not found")
        mock_client_class.return_value.__enter__.return_value = mock_client
        
        provider.get_token = Mock(return_value="test-token")
        
        user = provider.get_user("invalid-id")
        
        assert user is None
    
    @patch("auth.providers.auth0.httpx.Client")
    def test_create_user_success(self, mock_client_class, provider):
        """Test creating a user successfully."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "user_id": "auth0|456",
            "email": "new@example.com"
        }
        mock_response.raise_for_status = Mock()
        
        mock_client = Mock()
        mock_client.post.return_value = mock_response
        mock_client_class.return_value.__enter__.return_value = mock_client
        
        provider.get_token = Mock(return_value="test-token")
        
        user_data = {
            "email": "new@example.com",
            "password": "SecurePass123!",
            "connection": "Username-Password-Authentication"
        }
        
        result = provider.create_user(user_data)
        
        assert result["user_id"] == "auth0|456"
        assert result["email"] == "new@example.com"
    
    @patch("auth.providers.auth0.httpx.Client")
    def test_update_user_success(self, mock_client_class, provider):
        """Test updating a user successfully."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "user_id": "auth0|123",
            "email": "updated@example.com"
        }
        mock_response.raise_for_status = Mock()
        
        mock_client = Mock()
        mock_client.patch.return_value = mock_response
        mock_client_class.return_value.__enter__.return_value = mock_client
        
        provider.get_token = Mock(return_value="test-token")
        
        user_data = {"email": "updated@example.com"}
        
        result = provider.update_user("auth0|123", user_data)
        
        assert result["email"] == "updated@example.com"
    
    @patch("auth.providers.auth0.httpx.Client")
    def test_delete_user_success(self, mock_client_class, provider):
        """Test deleting a user successfully."""
        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        
        mock_client = Mock()
        mock_client.delete.return_value = mock_response
        mock_client_class.return_value.__enter__.return_value = mock_client
        
        provider.get_token = Mock(return_value="test-token")
        
        result = provider.delete_user("auth0|123")
        
        assert result is True
    
    @patch("auth.providers.auth0.httpx.Client")
    def test_delete_user_failure(self, mock_client_class, provider):
        """Test delete_user returns False on error."""
        import httpx
        
        mock_client = Mock()
        mock_client.delete.side_effect = httpx.HTTPError("Not found")
        mock_client_class.return_value.__enter__.return_value = mock_client
        
        provider.get_token = Mock(return_value="test-token")
        
        result = provider.delete_user("invalid-id")
        
        assert result is False
    
    @patch("auth.providers.auth0.httpx.Client")
    def test_get_clients_success(self, mock_client_class, provider):
        """Test getting clients successfully."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "clients": [{"client_id": "123", "name": "Test Client"}],
            "total": 1
        }
        mock_response.raise_for_status = Mock()
        
        mock_client = Mock()
        mock_client.get.return_value = mock_response
        mock_client_class.return_value.__enter__.return_value = mock_client
        
        provider.get_token = Mock(return_value="test-token")
        
        result = provider.get_clients(page=0, per_page=50)
        
        assert "clients" in result
        assert len(result["clients"]) == 1
    
    @patch("auth.providers.auth0.httpx.Client")
    def test_health_check_success(self, mock_client_class, provider):
        """Test health check returns True when API is accessible."""
        mock_response = Mock()
        mock_response.status_code = 200
        
        mock_client = Mock()
        mock_client.get.return_value = mock_response
        mock_client_class.return_value.__enter__.return_value = mock_client
        
        provider.get_token = Mock(return_value="test-token")
        
        result = provider.health_check()
        
        assert result is True
    
    @patch("auth.providers.auth0.httpx.Client")
    def test_health_check_returns_false_on_error(self, mock_client_class, provider):
        """Test health check returns False when API is unavailable."""
        provider.get_token = Mock(return_value=None)
        
        result = provider.health_check()
        
        assert result is False
