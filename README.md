# Deep Thought

> "The Answer to the Great Question... Of Life, the Universe and Everything... Is... Forty-two." - Deep Thought, after 7.5 million years of computation

Deep Thought is an AI-powered sales deal intelligence platform that helps sales teams navigate complex enterprise security deals with confidence. Built for Cyera's DSPM and DLP solutions, it provides a visual canvas for deal management, AI-powered persona simulation, and intelligent deal guidance.

## Vision

Every enterprise security deal involves multiple stakeholders, documents, meetings, technical discussions, and strategic decisions. Deep Thought provides a unified workspace where sales teams can:

- **Visualize the entire deal** on a node-based canvas
- **Simulate conversations** with key personas using Claude AI
- **Get intelligent guidance** on deal strategy, next steps, and win probability
- **Practice and experiment** in a safe, simulated environment
- **Track everything** that matters for deal success

## Core Concepts

### The Canvas
Each deal gets its own canvas - a visual workspace where you can add and organize:
- **People/Personas** - Key stakeholders with roles, LinkedIn, notes, and chat simulation
- **Documents** - RFIs, questionnaires, security assessments
- **Meetings** - Notes, attendees, decisions, action items
- **Integrations** - Salesforce opportunities, support issues, feature requests
- **Context** - Any information relevant to closing the deal

### AI-Powered Intelligence
Deep Thought uses Claude Opus to provide:
1. **Persona Chat Simulation** - Practice conversations with stakeholders based on their role and deal context
2. **Sales Assistant** - Ask questions, get guidance, brainstorm strategies
3. **Deal Scorecard** - MEDDPICC and Force Management analysis with win probability
4. **Product Intelligence** - Answers about Cyera's products and competitive positioning

### Collaboration
- Share canvases with team members (read-only or read-write)
- Chat histories saved for review and learning
- Sales managers get visibility across all deals

## Key Features

### MVP (Phase 1)
- Node-based canvas with drag-and-drop interface
- Generic and structured node types (Person, Meeting, Document, etc.)
- Basic AI chat with canvas context
- SAML authentication (Okta/Authentik)
- Canvas sharing and permissions
- JSON export/import

### Future Phases
- Salesforce integration
- Meeting transcript integration
- MCP server support for product questions
- Deal scorecard and reporting
- Background task processing
- Advanced node types (Support Issues, POCs, Feature Requests)

## Architecture

- **Frontend:** React + React Flow for canvas
- **Backend:** Python + FastAPI
- **Database:** SQLite (with PostgreSQL/MariaDB support planned)
- **AI:** Claude via AWS Bedrock (migrating to direct Anthropic API)
- **Auth:** SAML 2.0
- **Deployment:** Docker containers

## Getting Started

See [Development Setup](docs/development/setup.md) for detailed instructions.

Quick start:
```bash
docker-compose up
```

## Documentation

- [Architecture](docs/architecture/) - System design and ADRs
- [API Documentation](docs/api/) - REST API reference
- [Development Guide](docs/development/) - Setup, contributing, testing
- [Node Types](docs/node-types/) - How to extend with new node types

## Contributing

See [CONTRIBUTING.md](docs/development/contributing.md)

## License

Proprietary - Cyera Inc.
