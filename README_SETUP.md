# Chat Application - Database and Auth Setup

## Overview
This application now includes database-backed chat persistence and authentication scaffolding.

## Features
- User authentication with JWT tokens
- Message persistence to PostgreSQL database
- WebSocket chat with authentication
- Room-based chat system
- Message history retrieval

## Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables
Create a `.env` file in the project root (see `.env.example`):
```
DATABASE_URL=postgresql+psycopg2://user:password@localhost:5432/chatdb
AUTH_SECRET=your-secret-key-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

### 3. Set up PostgreSQL Database
Make sure PostgreSQL is running and create the database:
```bash
createdb chatdb
```

### 4. Run Database Migrations
```bash
alembic upgrade head
```

### 5. Run the Application
```bash
uvicorn app.main:app --reload
```

## API Endpoints

### Authentication
- `POST /auth/signup` - Register a new user
- `POST /auth/login` - Login and receive JWT token
- `POST /auth/logout` - Logout (clears cookie)
- `GET /auth/me` - Get current user info

### Chat Rooms
- `POST /rooms` - Create a new chat room (requires auth)
- `GET /rooms/{room_id}/messages?limit=50` - Get message history

### WebSocket
- `WS /ws/{room_id}?token=<jwt_token>` - Connect to chat room (requires auth)

## Database Models

### User
- id, username, email, hashed_password

### Chatroom
- id, name, theme

### Message
- id, room_id, user_id, role, content, created_at

### Session
- id, user_id, created_at, expires_at

### Persona
- id, name, system_prompt, style

### Theme
- id, name, description

## Testing
Run the test suite:
```bash
pytest
```

## Migration Commands
- Create a new migration: `alembic revision --autogenerate -m "description"`
- Apply migrations: `alembic upgrade head`
- Rollback migration: `alembic downgrade -1`
