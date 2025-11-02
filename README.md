# python_ai_chatroom
A chatroom with AI personalities

## Features
- Real-time WebSocket chat with message persistence
- User authentication with JWT tokens
- PostgreSQL database with SQLAlchemy ORM
- Room-based chat system
- Message history retrieval
- Alembic database migrations

## Quick Start

See [README_SETUP.md](README_SETUP.md) for detailed setup instructions.

### Installation
```bash
pip install -r requirements.txt
```

### Configuration
Copy `.env.example` to `.env` and update the values.

### Database Setup
```bash
alembic upgrade head
```

### Run
```bash
uvicorn app.main:app --reload
```

### Testing
```bash
pytest
```



