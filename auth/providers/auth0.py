"""
Auth0 Management API provider implementation.
Implements the AuthProvider interface for Auth0.
"""
import httpx
from typing import Dict, Any, Optional
from config import settings
from auth.providers.base import AuthProvider
from logger import logger


class Auth0Provider(AuthProvider):
    """
    Auth0 Management API provider.
    
    This class implements the AuthProvider interface for Auth0,
    allowing interaction with Auth0's Management API.
    """
    
    def __init__(self):
        """Initialize the Auth0 provider with configuration."""
        self.domain = settings.auth0_domain
        self.api_audience = settings.auth0_api_audience
        self.management_token = settings.auth0_management_token
        self.client_id = settings.auth0_client_id
        self.client_secret = settings.auth0_client_secret
        self.base_url = f"https://{self.domain}/api/v2"
    
    def get_token(self) -> Optional[str]:
        """
        Get or retrieve an authentication token.
        
        If a management token is configured, it will be used.
        Otherwise, a new token will be requested using client credentials.
        
        Returns:
            Optional[str]: The authentication token, or None if unavailable.
        """
        if self.management_token:
            return self.management_token
        
        # Validation
        if not all([self.domain, self.client_id, self.client_secret, self.api_audience]):
            logger.error("Missing Auth0 configuration for Management Token retrieval.")
            return None
        
        try:
            token_url = f"https://{self.domain}/oauth/token"
            payload = {
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "audience": self.api_audience,
                "grant_type": "client_credentials"
            }
            
            with httpx.Client() as client:
                response = client.post(token_url, json=payload, timeout=10.0)
                response.raise_for_status()
                data = response.json()
                return data.get("access_token")
        except httpx.HTTPError as e:
            logger.error(f"HTTP error obtaining management token: {e}")
            if e.response:
                logger.error(f"Response details: {e.response.text}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error obtaining management token: {e}")
            return None
    
    def authenticate_user(
        self,
        username: str,
        password: str,
        connection: str = "Username-Password-Authentication"
    ) -> Optional[Dict[str, Any]]:
        """
        Authenticate a user using Resource Owner Password Credentials Grant.
        
        Args:
            username: User's email or username.
            password: User's password.
            connection: Database connection name.
            
        Returns:
            Optional[Dict[str, Any]]: Token response containing access_token, or None if failed.
        """
        if not self.client_id or not self.client_secret:
            logger.error("Missing Client ID or Secret for user authentication.")
            return None
            
        url = f"https://{self.domain}/oauth/token"
        payload = {
            "grant_type": "http://auth0.com/oauth/grant-type/password-realm",
            "username": username,
            "password": password,
            "audience": self.api_audience,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "scope": "openid profile email offline_access",
            "realm": connection, 
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(url, json=payload, timeout=10.0)
                if response.status_code == 200:
                    return response.json()
                
                error_detail = response.json()
                error_msg = error_detail.get("error_description", "Authentication failed")
                logger.error(f"Authentication failed for user {username}: {error_msg}")
                logger.debug(f"Full error response: {error_detail}")
                
                return {"error": error_msg}
        except httpx.HTTPError as e:
            logger.error(f"HTTP error during authentication for user {username}: {e}")
            return {"error": str(e)}
    
    def _get_headers(self) -> Dict[str, str]:
        """
        Get HTTP headers with authorization token.
        
        Returns:
            Dict[str, str]: Headers dictionary with Authorization header.
        """
        token = self.get_token()
        if not token:
            raise ValueError("Unable to obtain authentication token")
        
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
    
    def get_users(
        self,
        page: int = 0,
        per_page: int = 50,
        include_totals: bool = False
    ) -> Dict[str, Any]:
        """
        Retrieve users from Auth0.
        
        Args:
            page: Page number for pagination (0-indexed).
            per_page: Number of users per page (max 100).
            include_totals: Whether to include total count.
            
        Returns:
            Dict[str, Any]: User data from Auth0.
        """
        url = f"{self.base_url}/users"
        params = {
            "page": page,
            "per_page": min(per_page, 100),
            "include_totals": str(include_totals).lower()
        }
        
        try:
            with httpx.Client() as client:
                response = client.get(
                    url,
                    headers=self._get_headers(),
                    params=params,
                    timeout=30.0
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            return {
                "error": str(e),
                "users": [],
                "total": 0
            }
    
    def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a specific user by ID.
        
        Args:
            user_id: The Auth0 user ID.
            
        Returns:
            Optional[Dict[str, Any]]: User data or None if not found.
        """
        url = f"{self.base_url}/users/{user_id}"
        
        try:
            with httpx.Client() as client:
                response = client.get(
                    url,
                    headers=self._get_headers(),
                    timeout=30.0
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError:
            return None
    
    def create_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new user in Auth0.
        
        Args:
            user_data: Dictionary containing user information.
                       Required fields: email, password, connection.
            
        Returns:
            Dict[str, Any]: Created user data.
        """
        url = f"{self.base_url}/users"
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    url,
                    headers=self._get_headers(),
                    json=user_data,
                    timeout=30.0
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            return {"error": str(e)}
    
    def update_user(
        self,
        user_id: str,
        user_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update an existing user.
        
        Args:
            user_id: The Auth0 user ID.
            user_data: Dictionary containing updated user information.
            
        Returns:
            Dict[str, Any]: Updated user data.
        """
        url = f"{self.base_url}/users/{user_id}"
        
        try:
            with httpx.Client() as client:
                response = client.patch(
                    url,
                    headers=self._get_headers(),
                    json=user_data,
                    timeout=30.0
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            return {"error": str(e)}
    
    def delete_user(self, user_id: str) -> bool:
        """
        Delete a user from Auth0.
        
        Args:
            user_id: The Auth0 user ID.
            
        Returns:
            bool: True if deletion was successful, False otherwise.
        """
        url = f"{self.base_url}/users/{user_id}"
        
        try:
            with httpx.Client() as client:
                response = client.delete(
                    url,
                    headers=self._get_headers(),
                    timeout=30.0
                )
                response.raise_for_status()
                return True
        except httpx.HTTPError:
            return False
    
    def get_clients(
        self,
        page: int = 0,
        per_page: int = 50,
        include_totals: bool = False
    ) -> Dict[str, Any]:
        """
        Retrieve clients from Auth0.
        
        Args:
            page: Page number for pagination (0-indexed).
            per_page: Number of clients per page (max 100).
            include_totals: Whether to include total count.
            
        Returns:
            Dict[str, Any]: Client data from Auth0.
        """
        url = f"{self.base_url}/clients"
        params = {
            "page": page,
            "per_page": min(per_page, 100),
            "include_totals": str(include_totals).lower()
        }
        
        try:
            with httpx.Client() as client:
                response = client.get(
                    url,
                    headers=self._get_headers(),
                    params=params,
                    timeout=30.0
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            return {
                "error": str(e),
                "clients": [],
                "total": 0
            }
    
    def health_check(self) -> bool:
        """
        Check if Auth0 Management API is accessible.
        
        Returns:
            bool: True if the API is accessible, False otherwise.
        """
        try:
            token = self.get_token()
            if not token:
                return False
            
            # Try to get users endpoint as health check
            url = f"{self.base_url}/users"
            with httpx.Client() as client:
                response = client.get(
                    url,
                    headers=self._get_headers(),
                    params={"per_page": 1},
                    timeout=10.0
                )
                # 200 or 401/403 is fine (means API is reachable)
                return response.status_code in [200, 401, 403]
        except Exception:
            return False
