<img width="1893" height="910" alt="Screenshot (198)" src="https://github.com/user-attachments/assets/5c70173e-141b-4387-be47-9cef69b3ecd6" />

# Polonium

An open-source, AI-powered collaborative workspace for developers to understand, discuss, and contribute to GitHub repositories.

## Features

- **Repository Connection**: Connect any GitHub repository (read-only)
- **Deep Understanding**: AI-powered repository structure parsing and indexing
- **Repository Overview**: AI-generated high-level architecture summaries
- **File Explanations**: Context-aware explanations for individual files
- **Collaborative Chat**: Real-time shared chat per repository with persistent history
- **Persistent Memory**: Repository-level AI memory that learns and remembers insights


## Architecture
### System Architecture

```mermaid
flowchart TD
    subgraph Clients["Clients"]
        A[Frontend Web App<br/>Next.js / TypeScript]
        B[CLI Client<br/>Python requests]
        C[Desktop Client<br/>Tauri / Rust wrapper]
    end

    subgraph Backend["Backend API (FastAPI)"]
        D[API Endpoints:<br/>/repositories<br/>/chat<br/>/health/metrics]
        E[Async SQLAlchemy]
        F[Pluggable AI Provider Factory<br/>LLM + Embedding]
    end

    subgraph Worker["Background Worker"]
        G[Celery Worker<br/>Ingestion tasks]
    end

    subgraph Storage["Storage & State"]
        H[(PostgreSQL<br/>System of Record)]
        I[(Qdrant<br/>Vector Store)]
        J[(Redis<br/>Cache + Celery broker/result)]
    end

    subgraph External["External Services"]
        K[GitHub API]
        L[LLM / Embedding Provider<br/>Pluggable]
    end

    %% Client → API
    A -->|REST / WS| D
    B -->|REST| D
    C -->|REST| D

    %% API → Storage (direct reads)
    D -->|read/write metadata| H
    D -->|read cache| J
    D -->|vector search| I

    %% API → Worker (ingestion trigger)
    D -->|queue repositories.ingest| G

    %% Worker → External/Storage
    G -->|fetch repo tree/files| K
    G -->|store files/memories| H
    G -->|generate embeddings| L
    G -->|upsert vectors| I
    G -->|cache results| J

    %% API → AI Provider (chat flow)
    D -->|embed query + LLM call| L

    %% Callouts
    style D fill:#e1f5fe
    style G fill:#fff3e0
    style H fill:#e8f5e9
    style I fill:#f3e5f5
    style J fill:#ffebee
    style L fill:#fce4ec

    %% Notes as annotations
    Note1[Async API + Prometheus metrics endpoint]
    Note2[WebSocket chat: placeholder echo]
    Note3[ARCHITECTURE.md referenced but missing]
    D -.-> Note1
    A -.-> Note2
    style Note3 fill:#fff9c4

Polonium follows a clean, modular architecture:

- **Frontend**: Next.js with TypeScript, Tailwind CSS, shadcn/ui, Monaco Editor
- **Backend**: FastAPI (Python) with async/await throughout
- **Database**: PostgreSQL for core data, Qdrant for vector embeddings, Redis for caching
- **AI**: OpenAI (swappable LLM abstraction), LangChain-ready

See [ARCHITECTURE.md](./ARCHITECTURE.md) for detailed architecture documentation.

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+ (for frontend)
- PostgreSQL 14+
- Redis 6+
- Qdrant (vector database)

### Backend Setup

1. Navigate to backend directory:
```bash
cd backend
```

2. Create virtual environment and install dependencies:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration (OpenAI API key, database URLs, etc.)
```

4. Set up databases:
- PostgreSQL: Create database `polonium`
- Qdrant: `docker run -p 6333:6333 qdrant/qdrant`
- Redis: `redis-server` (or use Docker)

5. Run migrations:
```bash
alembic upgrade head
```

6. Start the server:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at http://localhost:8000
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
# or
yarn install
# or
pnpm install
```

3. Set up environment variables:
```bash
cp .env.example .env.local
# Edit .env.local if needed (default API URL is http://localhost:8000)
```

4. Start the development server:
```bash
npm run dev
# or
yarn dev
# or
pnpm dev
```

The frontend will be available at http://localhost:3000

## Development

### Project Structure

```
Polonium/
├── backend/           # FastAPI backend
│   ├── app/
│   │   ├── api/       # API routes
│   │   ├── core/      # Configuration
│   │   ├── models/    # Database models
│   │   ├── schemas/   # Pydantic schemas
│   │   ├── services/  # Business logic
│   │   └── main.py    # FastAPI app
│   ├── alembic/       # Database migrations
│   └── requirements.txt
├── frontend/          # Next.js frontend (coming soon)
├── ARCHITECTURE.md    # Architecture documentation
└── README.md
```

### API Endpoints

#### Repositories
- `POST /api/v1/repositories` - Connect a GitHub repository
- `GET /api/v1/repositories` - List all repositories
- `GET /api/v1/repositories/{id}` - Get repository details
- `GET /api/v1/repositories/{id}/overview` - Get AI-generated overview

#### Files
- `GET /api/v1/repositories/{id}/files` - List files
- `GET /api/v1/repositories/{id}/files/{path}` - Get file details
- `GET /api/v1/repositories/{id}/files/{path}/explain` - Get AI file explanation

#### Chat
- `POST /api/v1/repositories/{id}/chat` - Send chat message
- `GET /api/v1/repositories/{id}/chat` - Get chat history
- `WS /api/v1/repositories/{id}/chat` - WebSocket for real-time chat

## Core Principles

- **Open-source first**: Everything is open and transparent
- **Modular architecture**: Clean separation of concerns
- **Beginner-friendly**: Clear code, good documentation
- **Self-hostable**: Run on your own infrastructure
- **Production-ready**: Security, error handling, scalability considered

## MVP Scope

**Included:**
- GitHub repo connection (read-only)
- Repo structure parsing and indexing
- AI-generated repo overview
- File-level AI explanations
- Shared chat per repo (persistent)
- Repo-level memory stored and reused by AI

**Not included (yet):**
- Project management tools
- Social feeds
- Payments
- Notifications
- IDE plugins

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

[To be determined - open source license]

## Status

✅ **MVP Complete** - Both backend and frontend are scaffolded and ready for development. Core features implemented:
- Repository connection and ingestion
- AI-powered overviews and file explanations
- Collaborative chat interface
- File browser with search

---

Your AI for making open source contribution and work more better and organized. so this is the preject and now i want to use the ai as a service what would be the opetion and also Iwant to lauch this product 
