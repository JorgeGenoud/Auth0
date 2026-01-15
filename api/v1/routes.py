"""
API v1 routes.
RESTful endpoints for user and client management.
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from auth.jwt_auth import get_current_user
from auth.providers import Auth0Provider
from config import settings
from schemas.auth import LoginRequest, TokenResponse
from schemas.user import UserCreate, UserUpdate

router = APIRouter(prefix="/api/v1", tags=["v1"])

# Initialize the authentication provider
auth_provider = Auth0Provider()


@router.get("/health")
async def health_check():
    """
    Health check endpoint.
    
    Returns:
        dict: Health status of the API and auth provider.
    """
    provider_healthy = auth_provider.health_check()
    
    return {
        "status": "healthy" if provider_healthy else "degraded",
        "api": "operational",
        "auth_provider": "operational" if provider_healthy else "unavailable",
        "provider_type": settings.auth_provider
    }


@router.post("/auth/login", response_model=TokenResponse)
async def login(login_request: LoginRequest):
    """
    Login endpoint.
    
    Authenticates the user against Auth0 using Resource Owner Password Grant.
    
    Args:
        login_request: Login credentials.
    
    Returns:
        TokenResponse: Access token.
        
    Raises:
        HTTPException: If authentication fails.
    """
    result = auth_provider.authenticate_user(
        username=login_request.username,
        password=login_request.password
    )
    
    if not result:
         raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication provider configuration error"
        )
        
    if "error" in result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=result.get("error")
        )
    
    return TokenResponse(
        access_token=result.get("access_token"),
        token_type=result.get("token_type", "bearer")
    )


@router.get("/users")
async def get_users(
    page: int = Query(default=0, ge=0, description="Page number"),
    per_page: int = Query(default=50, ge=1, le=100, description="Items per page"),
    include_totals: bool = Query(default=False, description="Include total count"),
    current_user: dict = Depends(get_current_user)
):
    """
    Get list of users from Auth0.
    
    Requires JWT authentication.
    
    Args:
        page: Page number for pagination (0-indexed).
        per_page: Number of users per page (max 100).
        include_totals: Whether to include total count.
        current_user: Current authenticated user (from JWT).
    
    Returns:
        dict: List of users from Auth0.
    """
    try:
        result = auth_provider.get_users(
            page=page,
            per_page=per_page,
            include_totals=include_totals
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving users: {str(e)}"
        )


@router.get("/users/{user_id}")
async def get_user(
    user_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get a specific user by ID.
    
    Requires JWT authentication.
    
    Args:
        user_id: Auth0 user ID.
        current_user: Current authenticated user (from JWT).
    
    Returns:
        dict: User data from Auth0.
    
    Raises:
        HTTPException: If user is not found.
    """
    user = auth_provider.get_user(user_id)
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User {user_id} not found"
        )
    
    return user


@router.post("/users", status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    current_user: dict = Depends(get_current_user)
):
    """
    Create a new user in Auth0.
    
    Requires JWT authentication.
    
    Args:
        user_data: User creation data.
        current_user: Current authenticated user (from JWT).
    
    Returns:
        dict: Created user data.
    
    Raises:
        HTTPException: If user creation fails.
    """
    user_dict = user_data.dict(exclude_none=True)
    
    try:
        result = auth_provider.create_user(user_dict)
        
        if "error" in result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("error", "Failed to create user")
            )
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating user: {str(e)}"
        )


@router.patch("/users/{user_id}")
async def update_user(
    user_id: str,
    user_data: UserUpdate,
    current_user: dict = Depends(get_current_user)
):
    """
    Update an existing user.
    
    Requires JWT authentication.
    
    Args:
        user_id: Auth0 user ID.
        user_data: Updated user data.
        current_user: Current authenticated user (from JWT).
    
    Returns:
        dict: Updated user data.
    
    Raises:
        HTTPException: If update fails.
    """
    user_dict = user_data.dict(exclude_none=True)
    
    if not user_dict:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No data provided for update"
        )
    
    try:
        result = auth_provider.update_user(user_id, user_dict)
        
        if "error" in result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("error", "Failed to update user")
            )
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating user: {str(e)}"
        )


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Delete a user from Auth0.
    
    Requires JWT authentication.
    
    Args:
        user_id: Auth0 user ID.
        current_user: Current authenticated user (from JWT).
    
    Raises:
        HTTPException: If deletion fails.
    """
    success = auth_provider.delete_user(user_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User {user_id} not found or could not be deleted"
        )


@router.get("/clients")
async def get_clients(
    page: int = Query(default=0, ge=0, description="Page number"),
    per_page: int = Query(default=50, ge=1, le=100, description="Items per page"),
    include_totals: bool = Query(default=False, description="Include total count"),
    current_user: dict = Depends(get_current_user)
):
    """
    Get list of clients from Auth0.
    
    Requires JWT authentication.
    
    Args:
        page: Page number for pagination (0-indexed).
        per_page: Number of clients per page (max 100).
        include_totals: Whether to include total count.
        current_user: Current authenticated user (from JWT).
    
    Returns:
        dict: List of clients from Auth0.
    """
    try:
        result = auth_provider.get_clients(
            page=page,
            per_page=per_page,
            include_totals=include_totals
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving clients: {str(e)}"
        )
