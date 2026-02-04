# ADR-005: Chat Context Isolation

## Status
Accepted

## Context
Users need to:
- Experiment with different approaches
- Practice conversations without "polluting" other contexts
- Have private conversations with personas
- Maintain chat history for review

However, users might also want to:
- Continue previous conversations
- Build on past insights

## Decision
Implement isolated chat sessions with optional continuation:

**Isolation Model**
- Each new chat starts with fresh context from canvas
- Previous chats don't influence new chats automatically
- Canvas changes don't reflect in active chats (snapshot model)
- Chat history stored with the node or canvas

**Continuation Support**
- Users can explicitly "continue from previous chat"
- When continuing, previous chat history is included in context
- Continuing shows which previous chat is being extended
- Users can rename chats for easy identification

**Storage**
- Chat histories stored indefinitely (text is cheap)
- Stored with the node (for persona chats) or canvas (for deal chats)
- Full conversation history, including system prompts and context

## Consequences

### Positive
- Clean experimentation without side effects
- Privacy between different scenarios
- Historical record of all interactions
- Explicit control over context continuity

### Negative
- Users might expect AI to "remember" across chats
- Need to explain snapshot behavior
- More chat management overhead

### Mitigation
- Clear UI indicators of chat isolation
- "Continue" button prominently displayed
- Chat renaming to help organization
- Documentation on best practices
- "Refresh context from canvas" option

## Implementation Details
- Chat session model: ID, canvas_id, node_id (optional), created_at, name, messages[]
- Message model: role, content, timestamp, token_count
- Default chat names: "Chat with [Person Name]" or "Sales Assistant [timestamp]"
- List view shows all chats with preview of last message
