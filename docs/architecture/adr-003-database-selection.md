# ADR-003: Database Selection and Migration Path

## Status
Accepted

## Context
Need a database solution that supports:
- 500-1000 users
- 10-20 concurrent users
- Canvas storage with nodes and chat history
- Easy deployment and backup
- Future scalability

## Decision
Start with SQLite, architect for PostgreSQL/MariaDB migration:

**Phase 1: SQLite**
- Single file database
- Zero configuration
- Built-in encryption support
- Simple backup/restore via admin UI
- Sufficient for initial scale

**Future: PostgreSQL/MariaDB**
- Use SQLAlchemy ORM for database abstraction
- Design schema to be portable
- Provide migration scripts
- Document upgrade path

## Consequences

### Positive
- Extremely simple initial deployment
- No separate database server to manage
- Perfect for Docker containerization
- Easy backup/restore for users
- SQLAlchemy makes future migration straightforward

### Negative
- SQLite has write concurrency limitations
- Not ideal for very high concurrent write loads
- Single file can be a single point of failure

### Mitigation
- With 10-20 concurrent users, SQLite is sufficient
- Most operations are reads (viewing canvases, chatting)
- Implement write queuing if needed
- Admin backup/restore ensures data safety
- Clear documentation on when to migrate to PostgreSQL

## Implementation Details
- Use SQLAlchemy Core/ORM
- Enable WAL mode for better concurrency
- Implement connection pooling
- Use SQLCipher for encryption
- Backup strategy: automated snapshots + manual export
