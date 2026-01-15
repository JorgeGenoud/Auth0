"""
Authentication providers module.
Implements Strategy pattern for multiple authentication providers.
"""

from auth.providers.base import AuthProvider
from auth.providers.auth0 import Auth0Provider

__all__ = ["AuthProvider", "Auth0Provider"]
