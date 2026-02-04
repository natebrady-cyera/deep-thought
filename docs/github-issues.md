# GitHub Issues for Deep Thought

## Labels to Create First

Create these labels in your repository:

- `mvp` - Must-have for initial demo (color: #d73a4a)
- `phase-2` - Post-MVP enhancements (color: #0075ca)
- `phase-3` - Future features (color: #cfd3d7)
- `node-type` - New node type (color: #a2eeef)
- `epic` - Major feature area (color: #7057ff)
- `enhancement` - Enhancement to existing feature (color: #84b6eb)
- `bug` - Bug fix (color: #d73a4a)
- `documentation` - Documentation (color: #0075ca)

## MVP Epic & Issues

### Epic: MVP - Basic Canvas and Chat

**Description:**
Core functionality needed to demonstrate Deep Thought to management. Focus on showing the canvas concept, basic node management, and AI chat integration.

**Issues under this epic:**

#### 1. Database Setup and Migrations
**Labels:** `mvp`, `backend`
**Description:**
- Set up SQLAlchemy with SQLite
- Create Alembic migrations for all models
- Implement database initialization
- Add health check for database connection

**Acceptance Criteria:**
- Database initializes on first run
- All models created correctly
- Migrations can be run forward and backward
- Health endpoint reports database status

---

#### 2. SAML Authentication Implementation
**Labels:** `mvp`, `backend`, `security`
**Description:**
Implement SAML 2.0 authentication with Okta/Authentik support.

**Tasks:**
- SAML SP metadata generation
- SAML ACS endpoint
- SAML login initiation
- Bootstrap admin user on first login
- JWT token generation and validation
- Auth middleware for protected endpoints

**Acceptance Criteria:**
- User can login via SAML
- First user with BOOTSTRAP_ADMIN_EMAIL becomes admin
- JWT tokens issued and validated correctly
- Protected endpoints require authentication

---

#### 3. Canvas CRUD Operations
**Labels:** `mvp`, `backend`, `frontend`
**Description:**
Complete implementation of canvas management.

**Backend Tasks:**
- Create canvas endpoint
- List canvases (user's + shared)
- Get canvas details
- Update canvas (name, description, viewport)
- Delete canvas
- Permission checking

**Frontend Tasks:**
- Canvas list page with create button
- Canvas card display (name, last modified, owner)
- Create canvas modal
- Delete confirmation
- Navigation to canvas

**Acceptance Criteria:**
- Users can create, view, list, and delete their canvases
- Shared canvases appear in list with visual indicator
- Canvas list shows owner and last modified date

---

#### 4. Generic Node Implementation
**Labels:** `mvp`, `backend`, `frontend`
**Description:**
Implement generic/freeform text nodes as the foundational node type.

**Backend Tasks:**
- Node CRUD endpoints
- Node position persistence
- Content size calculation
- Status indicators support

**Frontend Tasks:**
- GenericNode component with resizable text area
- Node toolbar (move, resize, delete)
- Add node button with node type selector
- Node drag-and-drop on canvas
- Node selection and focus

**Acceptance Criteria:**
- Users can add generic nodes to canvas
- Nodes can be moved and resized
- Node content persists
- Canvas saves node positions

---

#### 5. Basic AI Chat Integration
**Labels:** `mvp`, `backend`
**Description:**
Integrate Claude via AWS Bedrock for basic chat functionality.

**Tasks:**
- AWS Bedrock client setup
- Chat session management
- Canvas context building
- Message history storage
- Token counting for cost tracking
- Basic error handling and retry logic

**Acceptance Criteria:**
- Chat sessions can be created
- Messages sent to Claude with canvas context
- Responses stored in database
- Token usage tracked

---

#### 6. Sales Assistant Chat UI
**Labels:** `mvp`, `frontend`
**Description:**
Build the main chat interface for deal-level conversations.

**Tasks:**
- Chat panel component (collapsible/expandable)
- Message list with user/assistant distinction
- Input field with send button
- Loading states during AI response
- Chat history display
- "What's Next" button triggering special prompt

**Acceptance Criteria:**
- Users can send messages and receive responses
- Chat history displays correctly
- What's Next generates recommendations
- Loading states provide feedback

---

#### 7. Frontend Polish for Demo
**Labels:** `mvp`, `frontend`, `ui/ux`
**Description:**
Polish the UI to be presentable for management demo.

**Tasks:**
- Consistent styling across components
- Loading indicators
- Error messages
- Empty states (no canvases, no nodes)
- Responsive layout
- Login page with tagline
- Navigation/header component

**Acceptance Criteria:**
- UI looks professional and polished
- All states handled gracefully
- Tagline visible on login: "The Answer to Life, the Universe, and Enterprise Sales Deals"

---

## Phase 2 Epics & Issues

### Epic: Structured Node Types

#### 8. Person/Persona Node
**Labels:** `phase-2`, `node-type`
**Description:**
Structured node for key stakeholders with chat simulation.

**Fields:**
- Name, title, company
- LinkedIn URL
- Role in deal
- Personality notes
- Things they've said
- General notes

**Features:**
- Tabbed interface (Info, Chat, Notes)
- Persona chat with role-based prompting
- Multiple chat sessions

---

#### 9. Meeting Notes Node
**Labels:** `phase-2`, `node-type`
**Description:**
Structured node for meeting documentation.

**Fields:**
- Meeting name
- Date/time
- Attendees (freeform or linked to Person nodes)
- Agenda
- Notes
- Action items
- Decisions made

---

#### 10. Document Node
**Labels:** `phase-2`, `node-type`
**Description:**
Node for RFIs, questionnaires, security assessments.

**Fields:**
- Document name
- Document type
- Upload or link
- Key points
- Status
- Related to (freeform reference)

---

#### 11. Salesforce Opportunity Node
**Labels:** `phase-2`, `node-type`, `integration`
**Description:**
Integration with Salesforce to pull opportunity data.

**Tasks:**
- Salesforce API client
- OAuth authentication
- Opportunity data fetching
- Background refresh
- Read-only display (write support later)

**Fields:**
- Opportunity ID (manual or search)
- Opportunity name, stage, amount, close date
- Account name
- Key contacts
- Last sync time
- Refresh button

---

### Epic: Canvas Sharing and Collaboration

#### 12. Canvas Sharing Implementation
**Labels:** `phase-2`, `backend`, `frontend`
**Description:**
Allow users to share canvases with read or read-write permissions.

**Backend:**
- Share canvas endpoint
- Permission model (read, read-write)
- Permission checking on all canvas operations
- List shared users

**Frontend:**
- Share modal with user search
- Permission selector
- Shared users list
- Visual indicator on shared canvases
- Owner transfer capability

---

#### 13. Sales Manager Dashboard
**Labels:** `phase-2`, `frontend`
**Description:**
Special view for sales managers to see all deals.

**Features:**
- List all canvases across organization
- Filter by owner, stage, last activity
- Read-only access to all canvases
- Deal health indicators

---

### Epic: Deal Intelligence and Reporting

#### 14. Deal Scorecard Implementation
**Labels:** `phase-2`, `backend`, `frontend`, `ai`
**Description:**
MEDDPICC and Force Management analysis.

**Backend:**
- Scorecard generation prompt
- Parse structured scorecard data
- Background generation
- Caching strategy

**Frontend:**
- Scorecard panel/report view
- Visual indicators for MEDDPICC elements
- Win probability display
- Next steps recommendations
- Refresh button

---

#### 15. Chat Session Management
**Labels:** `phase-2`, `frontend`
**Description:**
Enhanced chat management features.

**Features:**
- Chat list view
- Rename chats
- Delete chats
- Continue from previous chat
- Chat timestamps
- Search within chat

---

## Phase 3 Epics & Issues

### Epic: Advanced Integrations

#### 16. Meeting Transcript Integration
**Labels:** `phase-3`, `integration`
**Description:**
Integration with meeting recording/transcription service.

---

#### 17. Provarity POC Integration
**Labels:** `phase-3`, `integration`
**Description:**
Link POC tracking from Provarity.

---

#### 18. MCP Server Support
**Labels:** `phase-3`, `backend`, `ai`
**Description:**
Support for multiple MCP servers for product questions.

**Features:**
- MCP client implementation
- Server registry in admin
- Server selection logic
- Usage instructions per server

---

### Epic: Additional Node Types

#### 19. Feature Request Node
**Labels:** `phase-3`, `node-type`

---

#### 20. Support Issue Node
**Labels:** `phase-3`, `node-type`

---

### Epic: System Administration

#### 21. Admin Panel - User Management
**Labels:** `phase-3`, `frontend`, `backend`
**Description:**
Full admin interface for user and system management.

---

#### 22. Admin Panel - System Configuration
**Labels:** `phase-3`, `frontend`, `backend`
**Description:**
Configure prompts, MCP servers, MEDDPICC framework.

---

#### 23. Backup and Restore
**Labels:** `phase-3`, `backend`
**Description:**
Automated backup and restore functionality.

---

#### 24. Audit Logging
**Labels:** `phase-3`, `backend`
**Description:**
Comprehensive audit trail of all actions.

---

### Epic: Advanced Features

#### 25. Canvas Search
**Labels:** `phase-3`, `frontend`, `backend`
**Description:**
Search across canvases and within nodes.

---

#### 26. Canvas Export/Import
**Labels:** `phase-3`, `backend`, `frontend`
**Description:**
JSON export/import for canvas backup and sharing.

---

#### 27. Canvas Cloning
**Labels:** `phase-3`, `backend`, `frontend`
**Description:**
Duplicate canvas for sandboxing.

---

#### 28. Canvas Archiving
**Labels:** `phase-3`, `backend`, `frontend`
**Description:**
Archive old/closed deals.

---

#### 29. PostgreSQL Migration Support
**Labels:** `phase-3`, `backend`, `documentation`
**Description:**
Documentation and tooling for SQLite to PostgreSQL migration.

---

## Milestones

1. **MVP Demo Ready** - Issues #1-7
2. **Phase 2 Complete** - Issues #8-15
3. **Phase 3 Complete** - Issues #16-29
4. **v1.0 Release** - All issues complete + testing + docs
