# Development Setup

## Prerequisites

- Docker and Docker Compose
- Node.js 18+ (for local frontend development)
- Python 3.11+ (for local backend development)
- Git

## Quick Start

1. Clone the repository:
```bash
git clone https://github.com/natebrady-cyera/deep-thought.git
cd deep-thought
```

2. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. Start the development environment:
```bash
docker-compose up
```

4. Access the application:
- Frontend: http://localhost:3000
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Local Development (without Docker)

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Environment Variables

### Required
- `SAML_IDP_METADATA_URL` - Your identity provider's SAML metadata URL
- `SAML_SP_ENTITY_ID` - Service provider entity ID (usually your app URL)
- `BOOTSTRAP_ADMIN_EMAIL` - Email of the first admin user

### Optional
- `AWS_BEDROCK_REGION` - AWS region for Bedrock (default: us-east-1)
- `AWS_BEDROCK_MODEL_ID` - Claude model ID (default: anthropic.claude-opus-4-20250514)
- `DATABASE_URL` - SQLite database path (default: ./data/deep-thought.db)
- `LOG_LEVEL` - Logging level (default: INFO)
- `API_RATE_LIMIT` - API rate limit per user (default: 100/minute)

## Database Migrations

```bash
cd backend
alembic upgrade head
```

## Testing

### Backend Tests
```bash
cd backend
pytest
```

### Frontend Tests
```bash
cd frontend
npm test
```

## Troubleshooting

### SAML Issues
- Verify your IdP metadata URL is accessible
- Check that SP entity ID matches your IdP configuration
- Review logs: `docker-compose logs backend`

### Database Issues
- Ensure data directory is writable
- Check SQLite file permissions
- Review database logs

### API Connection Issues
- Verify backend is running: `curl http://localhost:8000/api/v1/health`
- Check CORS configuration if frontend can't connect
- Review browser console for errors
