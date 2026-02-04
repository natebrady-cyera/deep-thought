"""
Deep Thought - AI-Powered Sales Deal Intelligence Platform

The Answer to Life, the Universe, and Enterprise Sales Deals.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.routers import auth, canvases, nodes, chats, admin, health

# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    description="AI-powered sales deal intelligence platform for enterprise security sales",
    version=settings.app_version,
    docs_url=f"{settings.api_prefix}/docs",
    redoc_url=f"{settings.api_prefix}/redoc",
    openapi_url=f"{settings.api_prefix}/openapi.json",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix=settings.api_prefix, tags=["health"])
app.include_router(auth.router, prefix=settings.api_prefix, tags=["auth"])
app.include_router(canvases.router, prefix=settings.api_prefix, tags=["canvases"])
app.include_router(nodes.router, prefix=settings.api_prefix, tags=["nodes"])
app.include_router(chats.router, prefix=settings.api_prefix, tags=["chats"])
app.include_router(admin.router, prefix=settings.api_prefix, tags=["admin"])


@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    # TODO: Initialize database
    # TODO: Check SAML configuration
    # TODO: Bootstrap admin user if needed
    pass


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    pass


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Deep Thought - The Answer to Life, the Universe, and Enterprise Sales Deals",
        "version": settings.app_version,
        "docs": f"{settings.api_prefix}/docs",
    }
