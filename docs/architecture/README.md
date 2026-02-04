# Architecture Documentation

This directory contains Architecture Decision Records (ADRs) documenting key technical decisions made during the development of Deep Thought.

## ADR Index

1. [ADR-001: Node-Based Canvas Architecture](adr-001-node-based-canvas.md)
2. [ADR-002: AI Context Management Strategy](adr-002-ai-context-management.md)
3. [ADR-003: Database Selection and Migration Path](adr-003-database-selection.md)
4. [ADR-004: Authentication and Authorization](adr-004-auth-system.md)
5. [ADR-005: Chat Context Isolation](adr-005-chat-context-isolation.md)
6. [ADR-006: API-First Design](adr-006-api-first-design.md)

## Architecture Principles

### Simplicity First
- Rely on AI to infer relationships rather than forcing rigid structures
- Support both structured and unstructured data
- Keep the UI clean and intuitive

### Extensibility
- Modular node type system
- Plugin-style architecture for integrations
- Clean internal interfaces for developers

### AI-Native Design
- Canvas provides context for all AI interactions
- Each chat session operates on canvas snapshot
- Background summarization for large contexts

### Collaboration Without Complexity
- Simple sharing model (read vs read-write)
- No real-time collaboration overhead
- Audit trails without version control complexity
