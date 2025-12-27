# Polonium Architecture

## High-Level Overview

Polonium is an AI-powered collaborative workspace for GitHub repositories. It provides deep repository understanding, persistent AI memory, and real-time collaborative chat.

## System Architecture

```
┌─────────────────┐
│   Next.js UI    │  (Frontend - to be implemented)
└────────┬────────┘
         │ HTTP/WebSocket
         ▼
┌─────────────────────────────────────────┐
│         FastAPI Backend                 │
│  ┌───────────────────────────────────┐  │
│  │  API Routes (REST + WebSocket)    │  │
│  └───────────┬───────────────────────┘  │
│              │                           │
│  ┌───────────▼───────────────────────┐  │
│  │      Service Layer                │  │
│  │  - GitHub Service                 │  │
│  │  - Repo Ingestion Service         │  │
│  │  - AI Service (LLM)               │  │
│  │  - Embedding Service              │  │
│  │  - Memory Service                 │  │
│  └───────────┬───────────────────────┘  │
│              │                           │
└──────────────┼───────────────────────────┘
               │
    ┌──────────┼──────────┐
    │          │          │
    ▼          ▼          ▼
┌─────────┐ ┌──────┐ ┌─────────┐
│PostgreSQL│ │Qdrant│ │  Redis  │
│  (Core)  │ │(Vec) │ │ (Cache) │
└─────────┘ └──────┘ └─────────┘
```

## Core Components

### 1. Repository Ingestion Pipeline
- **GitHub API Integration**: Fetch repository structure and files
- **File Parsing**: Extract code, comments, and metadata
- **Embedding Generation**: Create vector embeddings for semantic search
- **Indexing**: Store in Qdrant for fast retrieval

### 2. AI Services
- **Repository Overview**: Generate high-level architecture summary
- **File Explanations**: Provide context-aware file descriptions
- **Chat Interface**: Conversational AI with repo context
- **Memory Management**: Store and retrieve repo-level context

### 3. Real-time Collaboration
- **WebSocket Server**: Handle concurrent chat connections
- **Message Persistence**: Store chat history per repository
- **Context Injection**: Include relevant repo context in AI responses

### 4. Data Models

#### Repository
- GitHub repo metadata (owner, name, URL)
- Ingestion status and timestamps
- Configuration settings

#### File
- File path and content
- File type and language
- Embedding reference (Qdrant ID)
- Metadata (size, last modified)

#### ChatMessage
- Repository association
- User information
- Message content and timestamp
- AI response context

#### RepositoryMemory
- Repository association
- Memory chunks (key insights, patterns, decisions)
- Embeddings for memory retrieval
- Timestamps and versioning

## API Design

### REST Endpoints
- `POST /api/v1/repositories` - Connect a GitHub repository
- `GET /api/v1/repositories/{repo_id}` - Get repo details
- `GET /api/v1/repositories/{repo_id}/overview` - Get AI-generated overview
- `GET /api/v1/repositories/{repo_id}/files/{file_path}` - Get file explanation
- `GET /api/v1/repositories/{repo_id}/chat` - Get chat history
- `POST /api/v1/repositories/{repo_id}/chat` - Send chat message

### WebSocket
- `ws://api/v1/repositories/{repo_id}/chat` - Real-time chat connection

## Security Considerations
- GitHub OAuth for authentication
- Repository access validation
- Rate limiting on API endpoints
- Input sanitization for file paths
- Secure storage of GitHub tokens

## Scalability
- Async/await throughout for I/O operations
- Connection pooling for databases
- Caching layer with Redis
- Vector search optimization in Qdrant

