"""
JWT Authentication module for FastAPI.
Provides dependencies and utilities for JWT-based authentication.
"""
from datetime import datetime, timedelta
from typing import Optional
import jwt
from jwt import ExpiredSignatureError, InvalidTokenError
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from config import settings


# Security scheme for Bearer token authentication
security = HTTPBearer()


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.
    
    Args:
        data: Dictionary containing data to encode in the token.
        expires_delta: Optional timedelta for token expiration.
                      If not provided, uses default from settings.
    
    Returns:
        str: Encoded JWT token.
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.jwt_access_token_expire_minutes
        )
    
    to_encode.update({"exp": expire, "iat": datetime.utcnow()})
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm
    )
    
    return encoded_jwt


def verify_token(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """
    Verify and decode a JWT token.
    
    Args:
        credentials: HTTPBearer credentials containing the token.
    
    Returns:
        dict: Decoded token payload.
    
    Raises:
        HTTPException: If token is invalid or expired.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        token = credentials.credentials
        
        # Get the signing key from Auth0 JWKS
        jwks_url = f"https://{settings.auth0_domain}/.well-known/jwks.json"
        
        try:
            jwks_client = jwt.PyJWKClient(jwks_url)
            signing_key = jwks_client.get_signing_key_from_jwt(token)
            
            payload = jwt.decode(
                token,
                signing_key.key,
                algorithms=[settings.jwt_algorithm],
                audience=settings.auth0_api_audience,
                issuer=f"https://{settings.auth0_domain}/"
            )
            return payload
        except Exception as e:
            # Fallback for local testing (optional, can be removed implementation)
            if settings.jwt_algorithm == "HS256":
                 payload = jwt.decode(
                    token,
                    settings.jwt_secret_key,
                    algorithms=[settings.jwt_algorithm]
                )
                 return payload
            raise e
            
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except (InvalidTokenError, Exception) as e:
        print(f"Token validation error: {e}") # basic logging
        raise credentials_exception


def get_current_user(token_data: dict = Depends(verify_token)) -> dict:
    """
    Get the current authenticated user from token.
    
    Args:
        token_data: Decoded token payload.
    
    Returns:
        dict: User information from token.
    """
    return token_data
