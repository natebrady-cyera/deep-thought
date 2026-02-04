"""
Deep Thought - AI-Powered Sales Deal Intelligence Platform

The Answer to Life, the Universe, and Enterprise Sales Deals.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import init_db
from app.routers import auth, canvases, nodes, chats, admin, health
import logging

logger = logging.getLogger(__name__)

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
    logger.info("Starting Deep Thought...")

    # Initialize database
    try:
        init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise

    # TODO: Check SAML configuration
    # TODO: Bootstrap admin user if needed

    logger.info("Deep Thought startup complete")


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
