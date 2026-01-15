"""
FastAPI main application.
Entry point for the Auth0 Management API REST service.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import settings
from api.v1.routes import router as v1_router

# Initialize FastAPI application
app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    description="RESTful API for Auth0 Management with JWT authentication",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(v1_router)


@app.get("/")
async def root():
    """
    Root endpoint.
    
    Returns:
        dict: API information.
    """
    return {
        "message": "Auth0 Management API",
        "version": settings.api_version,
        "docs": "/docs",
        "health": "/api/v1/health"
    }


@app.get("/api/v1")
async def api_info():
    """
    API information endpoint.
    
    Returns:
        dict: API version and information.
    """
    return {
        "api_version": settings.api_version,
        "provider": settings.auth_provider,
        "endpoints": {
            "health": "/api/v1/health",
            "users": "/api/v1/users",
            "clients": "/api/v1/clients",
            "auth": "/api/v1/auth/login"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )
