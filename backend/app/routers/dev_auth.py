"""
Development authentication endpoints.

WARNING: These endpoints bypass SAML and should ONLY be used in development.
DO NOT enable in production!
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from app.core.database import get_db
from app.core.config import settings
from app.services.user_service import bootstrap_admin_if_needed
from app.services.jwt_service import create_access_token
import logging

logger = logging.getLogger(__name__)

# Only create this router if in debug mode
router = APIRouter(prefix="/dev-auth", tags=["dev-auth"])


class DevLoginRequest(BaseModel):
    """Development login request"""
    email: EmailStr
    full_name: str | None = None


@router.post("/login")
async def dev_login(
    login_req: DevLoginRequest,
    db: Session = Depends(get_db)
):
    """
    Development-only login endpoint that bypasses SAML.

    Creates or gets a user and issues a JWT token.

    WARNING: This endpoint should only be used in development!

    Args:
        login_req: Login request with email
        db: Database session

    Returns:
        JWT access token
    """
    if not settings.debug:
        raise HTTPException(
            status_code=404,
            detail="Not found"
        )

    # Bootstrap admin or create/get user
    user = bootstrap_admin_if_needed(
        db,
        email=login_req.email,
        full_name=login_req.full_name
    )

    # Create JWT token
    token_data = {
        "sub": str(user.id),
        "email": user.email,
        "role": user.role.value,
    }
    access_token = create_access_token(token_data)

    logger.info(f"DEV LOGIN: User {user.email} authenticated")

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role.value,
        }
    }
