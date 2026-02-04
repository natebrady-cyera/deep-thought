# ADR-002: AI Context Management Strategy

## Status
Accepted

## Context
Claude has context window limits. Complex deals may have dozens of nodes with substantial content. We need a strategy to provide relevant context without hitting limits or incurring unnecessary costs.

## Decision
Implement a multi-layered context management approach:

1. **Node Size Tracking**: Each node tracks its content size
2. **Automatic Summarization**: Nodes exceeding a threshold are summarized before being added to context
3. **Optional Exclusion**: Users can mark nodes to exclude from chat context
4. **Persona Lens**: For persona chats, context is filtered through that person's perspective
5. **Chat Isolation**: Each chat session operates on a snapshot of the canvas at chat start time

## Consequences

### Positive
- Scalable to large, complex deals
- Cost-effective token usage
- Users maintain control over what AI sees
- Prevents context confusion between chats

### Negative
- Summarization may lose important nuance
- Users need to understand exclusion feature
- Chat doesn't see real-time canvas updates

### Mitigation
- Clear UI indicators for summarized nodes
- Warning messages before summarization
- "Refresh context" option in ongoing chats
- Documentation on best practices

## Implementation Details
- Summarization threshold: TBD (start with ~5000 characters per node)
- Summary format: Structured key points that preserve data types
- Exclusion default: All nodes included unless explicitly excluded
