"""Authentication endpoints"""
from fastapi import APIRouter, Depends, HTTPException, status, Request, Form
from fastapi.responses import RedirectResponse, Response
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.saml_service import init_saml_auth, parse_saml_response, get_saml_settings
from app.services.user_service import bootstrap_admin_if_needed, update_user_saml_info
from app.services.jwt_service import create_access_token
from app.dependencies import get_current_user
from app.models.user import User
from onelogin.saml2.settings import OneLogin_Saml2_Settings
from typing import Optional
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth")


def prepare_request_data(request: Request) -> dict:
    """
    Convert FastAPI request to OneLogin SAML format.

    Args:
        request: FastAPI request object

    Returns:
        Dictionary with request data for OneLogin SAML
    """
    return {
        'https': 'on' if request.url.scheme == 'https' else 'off',
        'http_host': request.url.hostname,
        'script_name': request.url.path,
        'server_port': str(request.url.port or (443 if request.url.scheme == 'https' else 80)),
        'get_data': dict(request.query_params),
        'post_data': {},  # Will be populated for POST requests
    }


@router.get("/saml/metadata")
async def saml_metadata():
    """
    Return SAML service provider metadata XML.

    This endpoint provides the SP metadata that should be configured
    in your identity provider (Okta, Authentik, etc.).
    """
    try:
        saml_settings = get_saml_settings()
        settings_obj = OneLogin_Saml2_Settings(saml_settings)
        metadata = settings_obj.get_sp_metadata()

        return Response(content=metadata, media_type="application/xml")
    except Exception as e:
        logger.error(f"Error generating SAML metadata: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate SAML metadata: {str(e)}"
        )


@router.get("/saml/login")
async def saml_login(request: Request, relay_state: Optional[str] = None):
    """
    Initiate SAML login flow.

    Redirects user to the identity provider for authentication.

    Args:
        request: FastAPI request
        relay_state: Optional URL to redirect to after successful login
    """
    try:
        request_data = prepare_request_data(request)
        auth = init_saml_auth(request_data)

        # Get SSO URL and redirect
        sso_url = auth.login(return_to=relay_state)

        return RedirectResponse(url=sso_url)
    except Exception as e:
        logger.error(f"Error initiating SAML login: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to initiate SAML login: {str(e)}"
        )


@router.post("/saml/acs")
async def saml_acs(
    request: Request,
    SAMLResponse: str = Form(...),
    RelayState: Optional[str] = Form(None),
    db: Session = Depends(get_db),
):
    """
    SAML Assertion Consumer Service endpoint.

    This endpoint receives the SAML response from the identity provider,
    validates it, creates or updates the user, and issues a JWT token.

    Args:
        request: FastAPI request
        SAMLResponse: SAML response from IdP
        RelayState: Optional relay state for redirect
        db: Database session

    Returns:
        Redirect to frontend with JWT token or error
    """
    try:
        # Prepare request data with POST data
        request_data = prepare_request_data(request)
        request_data['post_data'] = {'SAMLResponse': SAMLResponse}
        if RelayState:
            request_data['post_data']['RelayState'] = RelayState

        # Initialize SAML auth and process response
        auth = init_saml_auth(request_data)
        auth.process_response()

        # Check for errors
        errors = auth.get_errors()
        if errors:
            error_reason = auth.get_last_error_reason()
            logger.error(f"SAML authentication failed: {errors}, reason: {error_reason}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"SAML authentication failed: {error_reason}"
            )

        # Check if user is authenticated
        if not auth.is_authenticated():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="SAML authentication failed"
            )

        # Parse SAML response to extract user attributes
        user_data = parse_saml_response(auth)

        if not user_data.get('email'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email not found in SAML response"
            )

        # Bootstrap admin or get/create user
        user = bootstrap_admin_if_needed(
            db,
            email=user_data['email'],
            full_name=user_data.get('full_name')
        )

        # Update SAML session info
        update_user_saml_info(
            db,
            user,
            saml_name_id=user_data.get('saml_name_id'),
            saml_session_index=user_data.get('saml_session_index')
        )

        # Create JWT token
        token_data = {
            "sub": str(user.id),
            "email": user.email,
            "role": user.role.value,
        }
        access_token = create_access_token(token_data)

        # Determine redirect URL
        redirect_url = RelayState or "/canvases"

        # For MVP, we'll redirect to a URL with token as query param
        # In production, you might want to use httpOnly cookies
        frontend_url = f"http://localhost:3000{redirect_url}?token={access_token}"

        logger.info(f"User {user.email} authenticated successfully via SAML")

        return RedirectResponse(url=frontend_url)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing SAML response: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process SAML response: {str(e)}"
        )


@router.post("/logout")
async def logout(current_user: User = Depends(get_current_user)):
    """
    Logout endpoint.

    For now, this is stateless (JWT tokens remain valid until expiry).
    In production, you might implement token blacklisting.

    Args:
        current_user: Current authenticated user

    Returns:
        Success message
    """
    logger.info(f"User {current_user.email} logged out")

    return {
        "message": "Logged out successfully",
        "note": "JWT token will remain valid until expiry. Delete it on the client side."
    }


@router.get("/me")
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    Get current user information.

    Args:
        current_user: Current authenticated user

    Returns:
        User information
    """
    return {
        "id": current_user.id,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "role": current_user.role.value,
        "is_active": current_user.is_active,
    }
