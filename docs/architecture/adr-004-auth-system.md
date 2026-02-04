# ADR-004: Authentication and Authorization

## Status
Accepted

## Context
Enterprise security company requires:
- SSO integration (Okta/Authentik)
- Role-based access control
- Canvas-level permissions
- Admin management capabilities

## Decision
Implement SAML 2.0 authentication with internal authorization:

**Authentication (SAML)**
- Okta or Authentik as identity provider
- SAML 2.0 for SSO
- Identity provider config via environment variables
- Bootstrap admin via environment variable email

**Authorization (Internal)**
- User roles: Admin, Sales Manager, User
- Canvas permissions: Owner, Read-Write, Read-Only
- Permission model:
  - Users see only their canvases + shared canvases
  - Sales Managers see all canvases (read-only)
  - Admins manage users, templates, system config

**Bootstrap Process**
- Environment variable: `BOOTSTRAP_ADMIN_EMAIL=admin@cyera.io`
- First SAML login with matching email becomes admin
- Admin can then assign roles to other users

## Consequences

### Positive
- Enterprise-grade SSO integration
- Flexible permission model
- Simple admin bootstrap
- Users can't bypass company authentication

### Negative
- SAML configuration complexity
- No local auth option (must have SAML provider)
- Admin bootstrap requires careful setup

### Mitigation
- Comprehensive SAML setup documentation
- Clear error messages during SAML issues
- Validation of bootstrap admin email
- Admin UI for role management

## Implementation Details
- Use python3-saml library
- JWT tokens for API session management
- Canvas permissions stored in database
- Role-based middleware for API endpoints
