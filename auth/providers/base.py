"""
Base class for authentication providers.
Implements the Strategy pattern to allow multiple authentication backends.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List


class AuthProvider(ABC):
    """
    Abstract base class for authentication providers.
    
    This class defines the interface that all authentication providers
    must implement, following the Strategy design pattern.
    """
    
    @abstractmethod
    def get_token(self) -> Optional[str]:
        """
        Retrieve an authentication token from the provider.
        
        Returns:
            Optional[str]: The authentication token, or None if unavailable.
        """
        pass
    
    @abstractmethod
    def get_users(
        self,
        page: int = 0,
        per_page: int = 50,
        include_totals: bool = False
    ) -> Dict[str, Any]:
        """
        Retrieve users from the authentication provider.
        
        Args:
            page: Page number for pagination (0-indexed).
            per_page: Number of users per page.
            include_totals: Whether to include total count.
            
        Returns:
            Dict[str, Any]: User data from the provider.
        """
        pass
    
    @abstractmethod
    def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a specific user by ID.
        
        Args:
            user_id: The unique identifier for the user.
            
        Returns:
            Optional[Dict[str, Any]]: User data or None if not found.
        """
        pass
    
    @abstractmethod
    def create_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new user in the authentication provider.
        
        Args:
            user_data: Dictionary containing user information.
            
        Returns:
            Dict[str, Any]: Created user data.
        """
        pass
    
    @abstractmethod
    def update_user(
        self,
        user_id: str,
        user_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update an existing user.
        
        Args:
            user_id: The unique identifier for the user.
            user_data: Dictionary containing updated user information.
            
        Returns:
            Dict[str, Any]: Updated user data.
        """
        pass
    
    @abstractmethod
    def delete_user(self, user_id: str) -> bool:
        """
        Delete a user from the authentication provider.
        
        Args:
            user_id: The unique identifier for the user.
            
        Returns:
            bool: True if deletion was successful, False otherwise.
        """
        pass
    
    @abstractmethod
    def get_clients(
        self,
        page: int = 0,
        per_page: int = 50,
        include_totals: bool = False
    ) -> Dict[str, Any]:
        """
        Retrieve clients from the authentication provider.
        
        Args:
            page: Page number for pagination (0-indexed).
            per_page: Number of clients per page.
            include_totals: Whether to include total count.
            
        Returns:
            Dict[str, Any]: Client data from the provider.
        """
        pass
    
    @abstractmethod
    def health_check(self) -> bool:
        """
        Check if the authentication provider is accessible.
        
        Returns:
            bool: True if the provider is healthy, False otherwise.
        """
        pass
