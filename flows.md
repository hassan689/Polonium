
###  Main Product Flow
```mermaid
flowchart TD
    U[User] --> AUTH[Login / Signup]
    AUTH --> DASH[Dashboard]
    DASH --> WS[Create / Open Workspace]
    WS --> REPO[Connect GitHub Repository]
    REPO --> INGEST[Repository Ingestion]
    INGEST --> INDEX[AI Indexing & Embeddings]
    INDEX --> READY[Workspace Ready]
    READY --> CHAT[Shared AI Chat]
    READY --> FILES[File Explorer]
    READY --> BRANCHES[Branches & Commits]
    CHAT --> MEM[Persistent Repo Memory]
    MEM --> CHAT
```

###  Repository Connection
```mermaid
flowchart LR
    U[User] --> WS[Workspace]
    WS --> GH[GitHub API]
    GH --> META[Repo Metadata]
    META --> WS
    GH --> TREE[Repo Tree]
    TREE --> WS
```

###  AI Indexing Process
```mermaid
flowchart TD
    REPO[GitHub Repo] --> TREE[Fetch Repo Tree]
    TREE --> FILTER[Ignore binaries & deps]
    FILTER --> CHUNK[Chunk files]
    CHUNK --> EMBED[Generate embeddings]
    EMBED --> VDB[(Vector Database)]
    TREE --> SUMMARY[AI Repo Summary]
    SUMMARY --> MEM[(Repo Memory)]
```

###  AI Q&A (RAG Flow)
```mermaid
sequenceDiagram
    participant User
    participant UI
    participant API
    participant VDB as Vector DB
    participant LLM
    participant MEM as Repo Memory
    User->>UI: Ask question
    UI->>API: Send query
    API->>VDB: Retrieve code
    API->>MEM: Load memory
    API->>LLM: Generate answer
    LLM->>API: AI response
    API->>UI: Show answer
```

###  Real-Time Collaboration
```mermaid
flowchart TD
    A[ Code Tree] --> B{Click Node}
    B --> C[Branch]
    B --> D[File]
    B --> E[Function]
    C --> F[ Open Chat Room]
    D --> F
    E --> F
    F --> G[ Real-time Chat]
    F --> H[ AI Assistance]
    G --> I[ Team Collaboration]
    H --> J[Code-aware Responses]
    I --> F
    J --> F
```

###  Memory Lifecycle
```mermaid
flowchart LR
    DISC[Discussion] --> DETECT[AI detects]
    DETECT --> SUM[Summarize]
    SUM --> CLASS[Classify]
    CLASS --> STORE[(Memory)]
    STORE --> EMBED[Embed]
    EMBED --> VDB[(Vector DB)]
    VDB --> FUTURE[Future AI]
```

###  Branch Analysis
```mermaid
flowchart TD
    GH[GitHub Webhook] --> EVT[Push Event]
    EVT --> BR[Detect branch]
    BR --> DIFF[Fetch diffs]
    DIFF --> REIDX[Re-index]
    REIDX --> VDB[(Vector DB)]
    REIDX --> MEM[(Repo Memory)]
```

###  System Architecture
```mermaid
flowchart LR
    FE[Frontend] --> BE[Backend]
    BE --> PG[(PostgreSQL)]
    BE --> VDB[(Qdrant)]
    BE --> REDIS[Redis]
    BE --> LLM[LLM Provider]
    BE --> GH[GitHub API]
```
