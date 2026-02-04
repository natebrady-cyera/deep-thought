# Extending Deep Thought with New Node Types

This guide explains how to add new node types to Deep Thought.

## Node Type Architecture

Each node type consists of:
1. **Backend Model** - Data structure and validation
2. **Frontend Component** - UI rendering and interaction
3. **Template Definition** - Default structure and fields

## Creating a New Node Type

### 1. Define the Backend Model

Create a new model in `backend/app/models/nodes/`:

```python
# backend/app/models/nodes/my_node.py
from sqlalchemy import Column, String, JSON
from app.models.base import BaseNode

class MyNodeData(BaseNode):
    __tablename__ = "my_node_data"

    # Specific fields for this node type
    custom_field = Column(String, nullable=True)
    metadata = Column(JSON, nullable=True)

    @property
    def content_size(self):
        """Calculate content size for context management"""
        size = len(self.custom_field or "")
        # Add other fields to size calculation
        return size

    def to_context_string(self):
        """Convert to string for AI context"""
        return f"Custom Field: {self.custom_field}\n..."
```

### 2. Create the Frontend Component

Create a component in `frontend/src/components/nodes/`:

```typescript
// frontend/src/components/nodes/MyNode.tsx
import React from 'react';
import { NodeProps } from 'reactflow';
import { BaseNode } from './BaseNode';

export const MyNode: React.FC<NodeProps> = ({ data, id }) => {
  return (
    <BaseNode
      id={id}
      title="My Node Type"
      icon="📝"
      data={data}
    >
      <div className="node-content">
        {/* Your custom UI here */}
        <input
          value={data.customField}
          onChange={(e) => data.onChange('customField', e.target.value)}
        />
      </div>
    </BaseNode>
  );
};
```

### 3. Register the Node Type

Add to `frontend/src/nodeTypes.ts`:

```typescript
import { MyNode } from './components/nodes/MyNode';

export const nodeTypes = {
  // ... existing types
  myNode: MyNode,
};

export const nodeTemplates = {
  // ... existing templates
  myNode: {
    label: 'My Node Type',
    icon: '📝',
    category: 'custom',
    defaultData: {
      customField: '',
    },
  },
};
```

### 4. Add API Endpoints

If your node type requires special API operations:

```python
# backend/app/routers/nodes/my_node.py
from fastapi import APIRouter, Depends
from app.models.nodes.my_node import MyNodeData
from app.dependencies import get_current_user

router = APIRouter(prefix="/api/v1/nodes/my-node", tags=["nodes"])

@router.post("/")
async def create_my_node(data: dict, user = Depends(get_current_user)):
    # Create node logic
    pass
```

## Node Type Guidelines

### Data Storage
- Store structured data in specific columns for querying
- Use JSON columns for flexible metadata
- Keep node content reasonable for AI context

### UI Design
- Extend BaseNode for consistent styling
- Support tabbed interface for complex nodes
- Show status indicators clearly
- Make actions discoverable

### Context Management
- Implement `content_size` property
- Implement `to_context_string()` for AI consumption
- Include only relevant information in context
- Consider summarization for large content

### API Integration
- Use background tasks for slow operations
- Provide progress indicators
- Handle API failures gracefully
- Cache external data appropriately

## Example: Support Ticket Node

See `backend/app/models/nodes/support_ticket.py` and `frontend/src/components/nodes/SupportTicket.tsx` for a complete example of a node type with:
- External API integration
- Background data fetching
- Status tracking
- Tabbed interface
- Context summarization

## Testing

Add tests for new node types:

```python
# backend/tests/test_my_node.py
def test_my_node_creation():
    # Test node creation
    pass

def test_my_node_context_string():
    # Test AI context generation
    pass
```

```typescript
// frontend/src/components/nodes/__tests__/MyNode.test.tsx
describe('MyNode', () => {
  it('renders correctly', () => {
    // Test rendering
  });
});
```
