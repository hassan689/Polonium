# Polonium Setup Guide

## Overview

This document provides step-by-step instructions to set up and run the Polonium backend.

## Prerequisites

- Python 3.11 or higher
- PostgreSQL 14+ (or use Docker)
- Redis 6+ (or use Docker)
- Qdrant vector database (or use Docker)
- OpenAI API key

## Quick Start with Docker

The easiest way to get started is using Docker Compose for the infrastructure:

```bash
# Start PostgreSQL, Redis, and Qdrant
docker-compose up -d

# Verify services are running
docker-compose ps
```

## Backend Setup

### 1. Create Virtual Environment

```bash
cd backend
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment

Create a `.env` file in the `backend` directory:

```bash
cp .env.example .env
```

Edit `.env` and set the following required variables:

```env
# Required
OPENAI_API_KEY=your_openai_api_key_here
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/polonium
REDIS_URL=redis://localhost:6379/0
QDRANT_URL=http://localhost:6333

# Optional (for GitHub OAuth - not yet implemented)
GITHUB_CLIENT_ID=your_github_client_id
GITHUB_CLIENT_SECRET=your_github_client_secret
```

### 4. Initialize Database

Option 1: Using Alembic (recommended for production):
```bash
alembic upgrade head
```

Option 2: Using the init script (for development):
```bash
python scripts/init_db.py
```

### 5. Start the Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- API: http://localhost:8000
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Testing the API

### 1. Connect a Repository

```bash
curl -X POST "http://localhost:8000/api/v1/repositories" \
  -H "Content-Type: application/json" \
  -d '{
    "owner": "microsoft",
    "name": "vscode"
  }'
```

This will:
- Create a repository record
- Start background ingestion (fetching files, generating embeddings)
- Generate an AI overview

### 2. Check Repository Status

```bash
curl "http://localhost:8000/api/v1/repositories/1"
```

Wait until `status` is `"completed"` before proceeding.

### 3. Get Repository Overview

```bash
curl "http://localhost:8000/api/v1/repositories/1/overview"
```

### 4. Get File Explanation

```bash
curl "http://localhost:8000/api/v1/repositories/1/files/src/main.py/explain"
```

### 5. Send Chat Message

```bash
curl -X POST "http://localhost:8000/api/v1/repositories/1/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "What is the main purpose of this repository?"
  }'
```

## Architecture Overview

### Services

- **GitHubService**: Fetches repository data from GitHub API
- **RepoIngestionService**: Orchestrates repository ingestion (files, embeddings, overview)
- **EmbeddingService**: Manages vector embeddings (OpenAI + Qdrant)
- **AIService**: Handles LLM interactions (overviews, explanations, chat)
- **MemoryService**: Manages persistent repository-level memory

### Data Flow

1. **Repository Connection**: User connects a GitHub repo
2. **Ingestion**: 
   - Fetch file tree from GitHub
   - Download file contents
   - Generate embeddings
   - Store in Qdrant
   - Generate AI overview
3. **Querying**:
   - User asks question
   - Semantic search finds relevant files/memories
   - AI generates response with context
   - Response stored in chat history

## Troubleshooting

### Database Connection Issues

- Verify PostgreSQL is running: `docker-compose ps`
- Check DATABASE_URL in `.env`
- Ensure database `polonium` exists: `createdb polonium`

### Qdrant Connection Issues

- Verify Qdrant is running: `curl http://localhost:6333/health`
- Check QDRANT_URL in `.env`

### OpenAI API Issues

- Verify OPENAI_API_KEY is set correctly
- Check API quota/limits
- Ensure you have credits

### Ingestion Fails

- Check repository is public or you have access token
- Verify GitHub API rate limits
- Check logs for specific file errors

## Next Steps

- Implement GitHub OAuth authentication
- Build Next.js frontend
- Add WebSocket real-time chat
- Implement memory extraction from conversations
- Add rate limiting and caching

## Development Tips

- Use `--reload` flag for auto-reload during development
- Check Swagger UI for interactive API testing
- Monitor database with `psql` or pgAdmin
- Check Qdrant dashboard at http://localhost:6333/dashboard

