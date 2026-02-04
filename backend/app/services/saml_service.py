"""
SAML authentication service.
"""
from onelogin.saml2.auth import OneLogin_Saml2_Auth
from onelogin.saml2.settings import OneLogin_Saml2_Settings
from app.core.config import settings
from typing import Dict, Any


def get_saml_settings() -> Dict[str, Any]:
    """
    Generate SAML settings for OneLogin SAML2 library.

    Returns:
        Dictionary with SAML configuration
    """
    # Construct ACS URL if not provided
    acs_url = settings.saml_acs_url
    if not acs_url:
        # Extract base URL from SP entity ID
        base_url = settings.saml_sp_entity_id.rstrip('/')
        acs_url = f"{base_url}/api/v1/auth/saml/acs"

    saml_settings = {
        "strict": True,
        "debug": settings.debug,
        "sp": {
            "entityId": settings.saml_sp_entity_id,
            "assertionConsumerService": {
                "url": acs_url,
                "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST"
            },
            "singleLogoutService": {
                "url": f"{settings.saml_sp_entity_id}/api/v1/auth/saml/sls",
                "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect"
            },
            "NameIDFormat": "urn:oasis:names:tc:SAML:1.1:nameid-format:emailAddress",
            "x509cert": "",  # Optional: SP certificate
            "privateKey": ""  # Optional: SP private key
        },
        "idp": {
            # IDP metadata URL will be fetched dynamically
        },
        "security": {
            "nameIdEncrypted": False,
            "authnRequestsSigned": False,
            "logoutRequestSigned": False,
            "logoutResponseSigned": False,
            "signMetadata": False,
            "wantMessagesSigned": False,
            "wantAssertionsSigned": False,
            "wantNameIdEncrypted": False,
            "requestedAuthnContext": True,
            "signatureAlgorithm": "http://www.w3.org/2001/04/xmldsig-more#rsa-sha256",
            "digestAlgorithm": "http://www.w3.org/2001/04/xmlenc#sha256",
        }
    }

    return saml_settings


def init_saml_auth(request_data: dict) -> OneLogin_Saml2_Auth:
    """
    Initialize SAML authentication object.

    Args:
        request_data: Dictionary with HTTP request data (post_data, get_data, etc.)

    Returns:
        OneLogin_Saml2_Auth instance
    """
    saml_settings = get_saml_settings()

    # Convert FastAPI request to OneLogin format
    req = {
        'https': 'on' if request_data.get('https') else 'off',
        'http_host': request_data.get('http_host', 'localhost'),
        'script_name': request_data.get('script_name', ''),
        'server_port': request_data.get('server_port', '443' if request_data.get('https') else '80'),
        'get_data': request_data.get('get_data', {}),
        'post_data': request_data.get('post_data', {}),
    }

    auth = OneLogin_Saml2_Auth(req, saml_settings)
    return auth


def parse_saml_response(auth: OneLogin_Saml2_Auth) -> dict:
    """
    Parse SAML response and extract user attributes.

    Args:
        auth: OneLogin_Saml2_Auth instance with processed response

    Returns:
        Dictionary with user attributes (email, name, etc.)
    """
    attributes = auth.get_attributes()
    name_id = auth.get_nameid()
    session_index = auth.get_session_index()

    # Extract email - try multiple common attribute names
    email = name_id  # Default to nameID
    for attr in ['email', 'mail', 'emailAddress', 'http://schemas.xmlsoap.org/ws/2005/05/identity/claims/emailaddress']:
        if attr in attributes and attributes[attr]:
            email = attributes[attr][0]
            break

    # Extract full name
    full_name = None
    for attr in ['displayName', 'cn', 'name', 'http://schemas.xmlsoap.org/ws/2005/05/identity/claims/name']:
        if attr in attributes and attributes[attr]:
            full_name = attributes[attr][0]
            break

    return {
        'email': email.lower() if email else None,
        'full_name': full_name,
        'saml_name_id': name_id,
        'saml_session_index': session_index,
        'attributes': attributes,
    }
