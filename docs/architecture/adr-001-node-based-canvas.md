# ADR-001: Node-Based Canvas Architecture

## Status
Accepted

## Context
Enterprise sales deals involve multiple stakeholders, documents, meetings, and interactions. Sales teams need a way to organize and visualize this information while maintaining context for AI-powered guidance.

## Decision
Use a node-based canvas architecture where:
- Each deal gets its own visual canvas
- Information is organized in moveable, resizable nodes
- Nodes have both structured and unstructured data
- Relationships are inferred by AI from content rather than explicitly defined
- React Flow provides the canvas implementation

## Consequences

### Positive
- Intuitive visual representation of deal complexity
- Flexible - works with structured or unstructured data
- Reduces cognitive load for sales teams
- Natural fit for AI context building
- React Flow is mature, well-maintained, and handles performance

### Negative
- More complex UI than a traditional form-based approach
- Mobile experience will be challenging
- Performance considerations with very large canvases

### Mitigation
- Start with desktop-first design
- Implement node content size warnings
- Lazy loading for large canvases
- Export/import for canvas management

## Alternatives Considered
1. **Traditional CRM-style forms** - Too rigid, doesn't reflect deal complexity
2. **Linear timeline view** - Doesn't capture multi-dimensional relationships
3. **Custom canvas from scratch** - Too much development overhead, React Flow is battle-tested
