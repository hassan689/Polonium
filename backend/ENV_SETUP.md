# Environment Variables Setup Guide

## Location

The `.env` file should be created in the **`backend/`** directory:

```
Polonium/
└── backend/
    ├── .env          ← Create this file here
    ├── app/
    ├── requirements.txt
    └── ...
```

## Quick Setup

### Create Manually

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```
2. **Create `.env` file:**
   - Windows: Create a new file named `.env` (use a text editor)
   - Mac/Linux: `touch .env`

3. **Add your credentials** (see template below)

## Environment Variables Template

Copy this template into your `.env` file and fill in your values:

```env
# Application
DEBUG=False

# Database
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/polonium

# Redis
REDIS_URL=redis://localhost:6379/0

# Qdrant
QDRANT_URL=http://localhost:6333
QDRANT_COLLECTION_NAME=polonium_embeddings

# Workspace Storage - Where cloned repositories are stored
WORKSPACE_STORAGE_PATH=./workspaces

# Local AI provider (OpenAI-compatible API format)
LOCAL_LLM_BASE_URL=http://localhost:11434/v1
LOCAL_LLM_API_KEY=
LOCAL_LLM_MODEL=llama3.1:8b
LOCAL_EMBEDDING_MODEL=nomic-embed-text
EMBEDDING_VECTOR_SIZE=768

# Security
SECRET_KEY=change-me-in-production-use-a-random-string-here
```

## Required Credentials

### 1. Local Model Endpoint (Required for AI Features)

Use a local model runtime that exposes OpenAI-compatible endpoints (for example Ollama/LM Studio).

Add to `.env`:
```env
LOCAL_LLM_BASE_URL=http://localhost:11434/v1
LOCAL_LLM_MODEL=llama3.1:8b
LOCAL_EMBEDDING_MODEL=nomic-embed-text
EMBEDDING_VECTOR_SIZE=768
```

### 3. Database (Required)

**Default (PostgreSQL):**
```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/polonium
```

**Change if your database credentials are different:**
```env
DATABASE_URL=postgresql+asyncpg://username:password@localhost:5432/database_name
```

## How to Edit .env File

### Windows:
1. Open Notepad or any text editor
2. Create new file
3. Save as `.env` (make sure it's not `.env.txt`)
4. Add your credentials
5. Save in `backend/` folder

### Mac/Linux:
```bash
cd backend
nano .env
# or
vim .env
# or use any text editor
```

## Example .env File

Here's a complete example with placeholder values:

```env
# Application
DEBUG=False

# Database
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/polonium

# Redis
REDIS_URL=redis://localhost:6379/0

# Qdrant
QDRANT_URL=http://localhost:6333
QDRANT_COLLECTION_NAME=polonium_embeddings

# GitHub OAuth
GITHUB_CLIENT_ID=Iv1.a1b2c3d4e5f6g7h8
GITHUB_CLIENT_SECRET=abc123def456ghi789jkl012mno345pqr678stu901vwx234
GITHUB_OAUTH_REDIRECT_URI=http://localhost:8000/api/v1/auth/github/callback

# Workspace Storage
WORKSPACE_STORAGE_PATH=./workspaces

# Local AI provider
LOCAL_LLM_BASE_URL=http://localhost:11434/v1
LOCAL_LLM_API_KEY=
LOCAL_LLM_MODEL=llama3.1:8b
LOCAL_EMBEDDING_MODEL=nomic-embed-text
EMBEDDING_VECTOR_SIZE=768

# Security
SECRET_KEY=my-super-secret-key-change-this-in-production-12345
ACCESS_TOKEN_EXPIRE_MINUTES=10080
```

## Important Notes

1. **Never commit `.env` to git** - It's already in `.gitignore`
2. **No spaces around `=`** - Use `KEY=value` not `KEY = value`
3. **No quotes needed** - Unless the value contains spaces
4. **Case sensitive** - Variable names are case-sensitive
5. **Restart server** - After changing `.env`, restart your backend server

## Verify Setup

After creating `.env`, verify it's working:

```bash
cd backend
python -c "from app.core.config import settings; print('GitHub Client ID:', settings.GITHUB_CLIENT_ID[:10] if settings.GITHUB_CLIENT_ID else 'Not set')"
```

## Troubleshooting

**File not found:**
- Make sure `.env` is in the `backend/` directory
- Check filename is exactly `.env` (not `.env.txt` or `env`)

**Variables not loading:**
- Restart your backend server
- Check for typos in variable names
- Ensure no spaces around `=`

**GitHub OAuth not working:**
- Verify `GITHUB_CLIENT_ID` and `GITHUB_CLIENT_SECRET` are set
- Check they match your GitHub OAuth App settings

