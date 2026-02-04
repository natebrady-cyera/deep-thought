# ADR-006: API-First Design

## Status
Accepted

## Context
The application should support:
- Web frontend (initial)
- Potential mobile apps (future)
- CLI tools (possible)
- Third-party integrations (future)

## Decision
Design the system with a comprehensive REST API that the frontend consumes:

**API Design Principles**
- All functionality available via API
- Frontend is a thin client
- OpenAPI/Swagger documentation
- Versioned endpoints (/api/v1/...)
- Standard HTTP methods and status codes
- JWT-based authentication after SAML

**API Structure**
```
/api/v1/auth/* - Authentication endpoints
/api/v1/canvases/* - Canvas CRUD and operations
/api/v1/nodes/* - Node operations
/api/v1/chats/* - Chat sessions and messaging
/api/v1/admin/* - Admin operations
/api/v1/integrations/* - Salesforce, etc.
/api/v1/health - Health check
```

**Documentation**
- OpenAPI 3.0 specification
- Auto-generated from FastAPI
- Interactive Swagger UI
- Code generation support for clients

## Consequences

### Positive
- Clean separation of concerns
- Easy to add new clients (mobile, CLI)
- Third-party integration ready
- API can be tested independently
- Self-documenting via OpenAPI

### Negative
- More upfront design work
- Need to maintain API compatibility
- Version management complexity

### Mitigation
- FastAPI makes API development fast
- OpenAPI auto-generation reduces documentation burden
- Semantic versioning for API changes
- Deprecation warnings before breaking changes

## Implementation Details
- FastAPI for API framework
- Pydantic models for request/response validation
- Auto-generated OpenAPI spec
- API versioning from day one
- Separate authentication from authorization
- Rate limiting per-user
- Request/response logging
