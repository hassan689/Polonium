# Polonium Backend

AI-powered collaborative workspace backend for GitHub repositories.

## Setup

### Prerequisites

- Python 3.11+
- PostgreSQL 14+
- Redis 6+
- Qdrant (vector database)

### Installation

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. Set up databases:
- PostgreSQL: Create database `polonium`
- Qdrant: Run `docker run -p 6333:6333 qdrant/qdrant` (or use existing instance)
- Redis: Run `redis-server` (or use existing instance)

5. Run database migrations:
```bash
alembic upgrade head
```

6. Start the development server:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## API Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Project Structure

```
backend/
├── app/
│   ├── api/           # API routes
│   │   └── v1/        # API version 1
│   ├── core/          # Core configuration
│   ├── models/        # Database models
│   ├── schemas/       # Pydantic schemas
│   ├── services/      # Business logic
│   └── main.py        # FastAPI app
├── alembic/           # Database migrations
├── requirements.txt
└── README.md
```

## Development

### Running Tests

```bash
# TODO: Add tests
```

### Database Migrations

Create a new migration:
```bash
alembic revision --autogenerate -m "description"
```

Apply migrations:
```bash
alembic upgrade head
```

### Code Style

This project follows PEP 8. Consider using:
- `black` for formatting
- `ruff` for linting
- `mypy` for type checking

