# Quick Testing Guide

## Step 1: Start the Backend Server

```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Step 2: Test Using One of These Methods

### Option A: Automated Test Script (Recommended)

```bash
# Test with default repository (facebook/react)
python test_cloning.py

# Test with custom repository
python test_cloning.py microsoft vscode
```

### Option B: Swagger UI (Interactive)

1. Open browser: http://localhost:8000/docs
2. Expand `POST /api/v1/repositories`
3. Click "Try it out"
4. Enter:
   ```json
   {
     "owner": "facebook",
     "name": "react"
   }
   ```
5. Click "Execute"
6. Copy the repository ID from response
7. Use `GET /api/v1/repositories/{id}` to check status

### Option C: cURL Commands

```bash
# Create repository
curl -X POST "http://localhost:8000/api/v1/repositories" \
  -H "Content-Type: application/json" \
  -d '{"owner": "facebook", "name": "react"}'

# Check status (replace 1 with your repo ID)
curl "http://localhost:8000/api/v1/repositories/1"

# List all repositories
curl "http://localhost:8000/api/v1/repositories"
```

## What to Expect

1. **Immediate Response**: Repository created with status "PENDING"
2. **After ~30 seconds**: Status changes to "IN_PROGRESS" 
3. **After 1-5 minutes**: Status changes to "COMPLETED"
4. **Check workspace**: Files cloned to `backend/workspaces/repo_{id}/`

## Troubleshooting

- **Server not starting?** Check if port 8000 is available
- **Status stuck at PENDING?** Check backend logs for errors
- **Git clone fails?** Ensure git is installed: `git --version`
- **Database errors?** Verify PostgreSQL is running and DATABASE_URL is correct

For detailed testing instructions, see [TESTING.md](TESTING.md)





