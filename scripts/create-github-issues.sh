#!/bin/bash
# Script to create GitHub issues for Deep Thought project
# Requires: gh CLI tool (https://cli.github.com/)
# Usage: ./create-github-issues.sh

set -e

REPO="natebrady-cyera/deep-thought"

echo "Creating labels..."

# Create labels
gh label create "mvp" --color "d73a4a" --description "Must-have for initial demo" --repo $REPO || true
gh label create "phase-2" --color "0075ca" --description "Post-MVP enhancements" --repo $REPO || true
gh label create "phase-3" --color "cfd3d7" --description "Future features" --repo $REPO || true
gh label create "node-type" --color "a2eeef" --description "New node type" --repo $REPO || true
gh label create "epic" --color "7057ff" --description "Major feature area" --repo $REPO || true
gh label create "backend" --color "d876e3" --description "Backend work" --repo $REPO || true
gh label create "frontend" --color "bfdadc" --description "Frontend work" --repo $REPO || true
gh label create "security" --color "ee0701" --description "Security related" --repo $REPO || true
gh label create "integration" --color "c2e0c6" --description "External integration" --repo $REPO || true
gh label create "ai" --color "fbca04" --description "AI/LLM related" --repo $REPO || true
gh label create "ui/ux" --color "e99695" --description "UI/UX improvements" --repo $REPO || true

echo "Labels created!"

echo "Creating MVP issues..."

# Issue 1: Database Setup
gh issue create --repo $REPO --title "Database Setup and Migrations" \
  --label "mvp,backend" \
  --body "Set up SQLAlchemy with SQLite and create initial database migrations.

**Tasks:**
- Set up SQLAlchemy with SQLite
- Create Alembic migrations for all models
- Implement database initialization
- Add health check for database connection

**Acceptance Criteria:**
- Database initializes on first run
- All models created correctly
- Migrations can be run forward and backward
- Health endpoint reports database status"

# Issue 2: SAML Authentication
gh issue create --repo $REPO --title "SAML Authentication Implementation" \
  --label "mvp,backend,security" \
  --body "Implement SAML 2.0 authentication with Okta/Authentik support.

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
- Protected endpoints require authentication"

# Issue 3: Canvas CRUD
gh issue create --repo $REPO --title "Canvas CRUD Operations" \
  --label "mvp,backend,frontend" \
  --body "Complete implementation of canvas management.

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
- Canvas list shows owner and last modified date"

# Issue 4: Generic Node
gh issue create --repo $REPO --title "Generic Node Implementation" \
  --label "mvp,backend,frontend" \
  --body "Implement generic/freeform text nodes as the foundational node type.

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
- Canvas saves node positions"

# Issue 5: AI Chat Integration
gh issue create --repo $REPO --title "Basic AI Chat Integration" \
  --label "mvp,backend,ai" \
  --body "Integrate Claude via AWS Bedrock for basic chat functionality.

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
- Token usage tracked"

# Issue 6: Sales Assistant Chat UI
gh issue create --repo $REPO --title "Sales Assistant Chat UI" \
  --label "mvp,frontend" \
  --body "Build the main chat interface for deal-level conversations.

**Tasks:**
- Chat panel component (collapsible/expandable)
- Message list with user/assistant distinction
- Input field with send button
- Loading states during AI response
- Chat history display
- \"What's Next\" button triggering special prompt

**Acceptance Criteria:**
- Users can send messages and receive responses
- Chat history displays correctly
- What's Next generates recommendations
- Loading states provide feedback"

# Issue 7: Frontend Polish
gh issue create --repo $REPO --title "Frontend Polish for Demo" \
  --label "mvp,frontend,ui/ux" \
  --body "Polish the UI to be presentable for management demo.

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
- Tagline visible on login: \"The Answer to Life, the Universe, and Enterprise Sales Deals\""

echo "MVP issues created!"
echo "See docs/github-issues.md for remaining Phase 2 and Phase 3 issues to create manually"
