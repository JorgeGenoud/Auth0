from pydantic import BaseModel

class LoginRequest(BaseModel):
    """Model for login request."""
    username: str
    password: str


class TokenResponse(BaseModel):
    """Model for token response."""
    access_token: str
    token_type: str = "bearer"
