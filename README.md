# python_ai_chatroom

An AI-powered multi-user chatroom built with FastAPI and WebSocket. Users can join chatrooms, interact with multiple AI personalities that respond in short chatroom-style messages, and have their conversations persisted. AI personalities follow user-supplied themes and can respond to both users and each other, creating dynamic group chat experiences.

## Features

- **Multi-user chatrooms**: Real-time WebSocket-based chat with join/leave notifications and message broadcasting
- **AI personalities**: Select from multiple AI personas with distinct styles, knowledge, and response patterns
- **Short, chatroom-style replies**: AIs respond concisely, mimicking natural chat behavior
- **Theme-based conversations**: User-supplied themes guide AI personality responses and behavior
- **Persisted sessions**: Chat messages, rooms, and user sessions stored in PostgreSQL for continuity
- **Browser-based UI**: Tailwind CSS-styled interface with real-time message display and user avatars
- **Phase 2: SMS extension** (roadmap): Extend chatroom interactions to SMS/text messaging with the same AI personalities

---

## Architecture

### High-level Components

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend Layer                          │
│  • assets/index.html (Tailwind UI, WebSocket client)        │
│  • frontend/templates/index.html (alternate template)       │
└────────────────────┬────────────────────────────────────────┘
                     │ HTTP / WebSocket
┌────────────────────▼────────────────────────────────────────┐
│                 FastAPI Application                         │
│                                                              │
│  Root Entrypoint (app.py):                                  │
│  • In-memory client registry (dict[str, Client])            │
│  • Asyncio broadcast queue (room_queue)                     │
│  • /chat WebSocket endpoint with user_id query param        │
│  • /clients GET endpoint (list active users)                │
│  • Serves assets/index.html at /                            │
│                                                              │
│  app/ Package Variant (app/main.py):                        │
│  • Database initialization on startup                       │
│  • /ws/{chatroom_id} WebSocket endpoint (echo mode)         │
│  • References app.auth (currently missing)                  │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│                 Persistence Layer                           │
│  • SQLAlchemy ORM with PostgreSQL                           │
│  • Models: User (username, email, hashed_password)          │
│  •         Chatroom (name, theme)                           │
│  • Planned: Message, Session, Persona, Theme, Membership    │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│              AI Orchestration Layer (Planned)               │
│  • Persona management (system prompts, style constraints)   │
│  • Theme controller (inject user theme into AI context)     │
│  • Response router (select AIs, turn-taking, conciseness)   │
│  • OpenAI or equivalent LLM provider integration            │
│  • Safety and moderation filters                            │
└─────────────────────────────────────────────────────────────┘
```

### Current State and Gaps

**What's Working:**
- In-memory WebSocket chatroom with real-time message broadcasting
- Join/leave system notifications
- Client connection management and asyncio-based message dispatch
- Tailwind-styled browser UI with avatar display and auto-scrolling
- SQLAlchemy models for User and Chatroom

**Known Gaps:**
- **app.auth module missing**: app/main.py imports `app.auth.get_current_user` but the module doesn't exist
- **Database not wired into chat flow**: Messages and users exist only in memory; SQLAlchemy models are defined but not used in root app.py
- **No AI integration**: Personality system, LLM provider, and orchestration layer not yet implemented
- **No persistence for messages**: room_queue and clients dict are in-memory; cleared on restart
- **No authentication or authorization**: WebSocket endpoint accepts any user_id without validation
- **Single global room**: Root app.py has one shared room_queue; no multi-room support

---

## Local Development

### Prerequisites

- **Python**: 3.11 or higher
- **PostgreSQL**: 14+ (optional for now; required when DB integration is complete)
- **Node.js** (optional): Only if rebuilding Tailwind CSS; current UI uses CDN

### Setup

1. **Clone the repository and create a virtual environment:**

   ```bash
   git clone <repository_url>
   cd python_ai_chatroom
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

2. **Install dependencies:**

   Create `requirements.txt` with:

   ```
   fastapi>=0.104.0
   uvicorn[standard]>=0.24.0
   sqlalchemy>=2.0.0
   psycopg2-binary>=2.9.9
   pydantic>=2.0.0
   python-dotenv>=1.0.0
   jinja2>=3.1.0
   websockets>=12.0
   openai>=1.3.0
   httpx>=0.25.0
   ```

   Then install:

   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables:**

   Create a `.env` file in the project root:

   ```env
   # Database
   DATABASE_URL=postgresql+psycopg2://user:password@localhost:5432/chatdb

   # Authentication
   AUTH_SECRET=your-secret-key-min-32-chars
   JWT_ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30

   # AI Provider
   OPENAI_API_KEY=sk-your-openai-api-key-here
   OPENAI_MODEL=gpt-4-turbo-preview

   # CORS and Security
   FRONTEND_ORIGIN=http://localhost:8000
   ALLOWED_ORIGINS=http://localhost:8000,http://localhost:3000

   # Optional: Rate limiting
   RATE_LIMIT_PER_USER=60
   RATE_LIMIT_WINDOW_SECONDS=60
   ```

4. **Set up PostgreSQL (optional, for future DB integration):**

   ```bash
   # Create database
   psql -U postgres
   CREATE DATABASE chatdb;
   CREATE USER user WITH PASSWORD 'password';
   GRANT ALL PRIVILEGES ON DATABASE chatdb TO user;
   \q
   ```

### Running the Application

**Option 1: Root entrypoint (current working version)**

```bash
# Run with asyncio-based server
python app.py

# Or use uvicorn directly (recommended for development)
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

Access the chat UI at: **http://localhost:8000**

**Option 2: app/ package entrypoint (database-backed, echo mode)**

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Note: This variant requires `app/auth.py` to be implemented and database to be running.

### Testing the Chat

1. Open http://localhost:8000 in your browser
2. Enter a username and click "Join"
3. Open another browser window or incognito tab with a different username
4. Messages sent from either client will appear in real-time on all connected clients
5. Join/leave notifications display when users connect or disconnect

---

## WebSocket API

### Endpoints

**Root app.py:**
- `ws://localhost:8000/chat?user_id={username}`

**app/main.py (DB variant):**
- `ws://localhost:8000/ws/{chatroom_id}`

### Message Schema

All messages follow a JSON envelope format:

```json
{
  "sender": "string",          // Username or @system for server messages
  "text": "string",            // Message content
  "ctime": "string",           // ISO 8601 timestamp or Unix time
  "event": "string"            // Message type: "user", "join", "leave", "system"
}
```

### Client → Server

**Send a chat message:**

Send plain text over the WebSocket connection:

```javascript
ws.send("Hello, everyone!");
```

The server wraps this in a Message object with sender, timestamp, and event type.

### Server → Client

**User message:**

```json
{
  "sender": "alice",
  "text": "Hey everyone!",
  "ctime": "2024-01-15T10:30:45",
  "event": "user"
}
```

**Join notification:**

```json
{
  "sender": "@system",
  "text": "alice joined",
  "ctime": "1705318245",
  "event": "join"
}
```

**Leave notification:**

```json
{
  "sender": "@system",
  "text": "alice leave",
  "ctime": "1705318300",
  "event": "leave"
}
```

**AI response (planned):**

```json
{
  "sender": "AI_Einstein",
  "text": "Fascinating question!",
  "ctime": "2024-01-15T10:30:50",
  "event": "ai",
  "persona_id": "einstein",
  "room_id": "room_123"
}
```

### Error Handling

- **User ID starts with `@`**: Connection rejected (reserved for system messages)
- **Duplicate user_id**: Connection rejected with 400 error
- **WebSocket disconnect**: Leave message broadcast, client removed from registry

---

## Data Model and Persistence Plan

### Existing Models

**User** (`app/models.py`)

```python
class User(Base):
    __tablename__ = "users"
    id: int (PK)
    username: str (unique, indexed)
    email: str (unique, indexed)
    hashed_password: str
```

**Chatroom** (`app/models.py`)

```python
class Chatroom(Base):
    __tablename__ = "chatrooms"
    id: int (PK)
    name: str
    theme: str  # User-supplied theme for AI personalities
```

### Planned Models

**Message**

```python
class Message(Base):
    __tablename__ = "messages"
    id: int (PK)
    chatroom_id: int (FK → chatrooms.id)
    user_id: int (FK → users.id, nullable)
    persona_id: int (FK → personas.id, nullable)
    content: str
    role: enum ('user', 'ai', 'system')
    created_at: datetime (indexed)
    edited_at: datetime (nullable)
    deleted_at: datetime (nullable, soft delete)
```

**Session**

```python
class Session(Base):
    __tablename__ = "sessions"
    id: int (PK)
    user_id: int (FK → users.id)
    token: str (unique, indexed)
    expires_at: datetime (indexed)
    created_at: datetime
    ip_address: str
    user_agent: str
```

**Persona**

```python
class Persona(Base):
    __tablename__ = "personas"
    id: int (PK)
    name: str (unique)
    display_name: str
    system_prompt: str
    style_constraints: json  # {"max_tokens": 50, "temperature": 0.7}
    is_active: bool
    created_by: int (FK → users.id, nullable for system personas)
```

**Theme**

```python
class Theme(Base):
    __tablename__ = "themes"
    id: int (PK)
    chatroom_id: int (FK → chatrooms.id)
    description: str
    active_persona_ids: json  # List of persona IDs active in this theme
    created_by: int (FK → users.id)
```

**Membership**

```python
class Membership(Base):
    __tablename__ = "memberships"
    id: int (PK)
    user_id: int (FK → users.id)
    chatroom_id: int (FK → chatrooms.id)
    role: enum ('member', 'moderator', 'admin')
    joined_at: datetime
    last_read_at: datetime (for unread counts)
```

### Session Persistence Behavior

1. **User connects**: Session token validated → User record loaded → Membership checked
2. **Message sent**: Stored in `messages` table with chatroom_id, user_id/persona_id, timestamp
3. **Room state**: Chatroom theme and active personas loaded on connect
4. **History**: Last N messages retrieved from DB on join
5. **Presence**: Redis sorted set tracks online users per room (TTL-based heartbeat)

---

## Authentication and Authorization

### Short-term (MVP)

- **Cookie-based sessions**: Signed session cookie with user_id and expiration
- **Minimal signup/login**: POST `/signup` (username, email, password) and `/login` (username/email, password)
- **Password hashing**: bcrypt or argon2 for hashed_password storage
- **WebSocket auth**: Session cookie validated in WebSocket handshake

### Mid-term (Production)

- **JWT tokens**: Access token (short-lived, 15min) + refresh token (long-lived, 7d)
- **Token storage**: Refresh tokens in `sessions` table with device tracking
- **CSRF protection**: SameSite cookies + CSRF tokens for state-changing forms
- **Password requirements**: Min 12 chars, complexity checks, breach detection (haveibeenpwned API)
- **Rate limiting**: Per-user and per-IP limits on login, signup, message send

### Authorization Model

**Roles:**
- `user`: Standard chatroom member (read messages, send messages, join public rooms)
- `moderator`: Room-level moderation (mute users, delete messages, kick users)
- `admin`: System-level admin (manage personas, themes, user accounts)

**Enforcement:**
- WebSocket messages checked against room membership before broadcast
- Room-level permissions enforced via `memberships.role`
- Admin endpoints require `is_admin` flag on User model

**Rate Limiting:**
- **Message send**: 60 messages per user per minute
- **Login attempts**: 5 failed attempts per IP per hour
- **API requests**: 100 requests per user per minute

---

## AI Personalities and Chat Orchestration

### Persona Definition

Each AI personality is defined by:

**Core Attributes:**
- `name`: Unique identifier (e.g., "einstein", "shakespeare")
- `display_name`: User-facing name ("Albert Einstein", "William Shakespeare")
- `system_prompt`: Base personality and knowledge scope
- `style_constraints`:
  ```json
  {
    "max_tokens": 50,
    "temperature": 0.7,
    "reply_format": "conversational",
    "tone": "friendly"
  }
  ```

**Example Persona:**

```python
{
  "name": "einstein",
  "display_name": "AI Einstein",
  "system_prompt": "You are Albert Einstein, the theoretical physicist. Respond with curiosity about the universe, relativity, and thought experiments. Keep replies very short (1-2 sentences) and conversational.",
  "style_constraints": {
    "max_tokens": 40,
    "temperature": 0.7,
    "personality_traits": ["curious", "thought-provoking", "humble"]
  }
}
```

### Theme Controller

Themes provide room-wide context for AI responses:

**Theme Structure:**

```python
{
  "chatroom_id": "room_123",
  "description": "A casual conversation about space exploration and future technologies",
  "guidelines": "Stay on topic; avoid politics; encourage creative thinking",
  "active_personas": ["einstein", "musk", "curie"]
}
```

**Theme Injection:**

When an AI responds, the theme is injected into the context:

```python
system_message = f"""
{persona.system_prompt}

Current chatroom theme: {theme.description}
Guidelines: {theme.guidelines}

Respond as {persona.display_name} in 1-2 short sentences, staying on theme.
"""
```

### Orchestration Loop

**Message Flow:**

1. **User sends message** → Stored in DB → Broadcast to all connected clients
2. **Router evaluates**: Should AI(s) respond? Which persona(s)?
   - Mention detection: "@einstein what do you think?"
   - Topic relevance: NLU checks if message relates to active personas
   - Turn-taking: Max 1 AI response per user message (configurable)
3. **Selected AI generates response**:
   - Context: Last 10 messages + theme + persona prompt
   - Constraint: max_tokens enforced (short replies)
   - Post-processing: Check for safety, PII redaction
4. **AI response** → Stored in DB → Broadcast as persona message

**Turn-Taking Policy:**

- **One response per user message**: Avoid AI flooding the chat
- **Round-robin selection**: Rotate through active personas
- **Mention override**: Direct @mentions trigger that specific persona
- **Cooldown**: AI can't respond twice in a row (encourage variety)

**Token Budget:**

- **Per-message budget**: 50 tokens per AI response
- **Context window**: Last 10 messages (≈500 tokens) + system prompt
- **Daily room limit**: 10,000 tokens per chatroom to control costs

### Safety and Moderation

**Input Filtering:**
- Block profanity, hate speech, harassment (regex + ML classifier)
- Detect and reject prompt injection attempts
- Rate limit message frequency per user

**Output Filtering:**
- Scan AI responses for inappropriate content before sending
- Redact PII (emails, phone numbers, addresses) using regex/NER
- Refusal fallback: If unsafe content generated, replace with "[Response filtered]"

**Logging:**
- All AI responses logged with prompt, response, tokens used, filter flags
- Flagged messages reviewed by moderators
- User reports trigger automated review workflow

---

## Phase 2: SMS Extension

### Architecture

```
User Phone → Twilio → Webhook → FastAPI → Chatroom
                                    ↓
                               AI Personas respond
                                    ↓
                            FastAPI → Twilio → User Phone
```

### Implementation Plan

**1. Twilio Integration**

- **Inbound webhook**: `POST /sms/incoming` receives message from Twilio
- **Outbound API**: Send AI responses via Twilio REST API
- **Phone mapping**: Link phone numbers to User records

**2. User/Phone Mapping**

```python
class PhoneNumber(Base):
    __tablename__ = "phone_numbers"
    id: int (PK)
    user_id: int (FK → users.id)
    phone_number: str (unique, E.164 format)
    verified: bool
    verification_code: str (nullable)
    opt_in_status: enum ('opted_in', 'opted_out', 'pending')
    consented_at: datetime
```

**3. SMS Flow**

**User sends SMS:**

```
User: "Hello everyone!"
  ↓
Twilio webhook → /sms/incoming
  ↓
Parse sender phone → Lookup User
  ↓
Create Message in chatroom
  ↓
Broadcast to WebSocket clients
  ↓
AI orchestration triggers response
  ↓
Send AI response via Twilio API to original phone
```

**Endpoint Example:**

```python
@app.post("/sms/incoming")
async def sms_incoming(
    From: str = Form(...),
    Body: str = Form(...),
    MessageSid: str = Form(...)
):
    # Lookup user by phone number
    phone = await get_phone_by_number(From)
    if not phone or phone.opt_in_status != 'opted_in':
        return TwiMLResponse("You are not registered.")
    
    # Store message in chatroom
    message = await create_message(
        chatroom_id=phone.user.default_room_id,
        user_id=phone.user_id,
        content=Body
    )
    
    # Broadcast to WebSocket clients
    await broadcast_message(message)
    
    # Trigger AI response (async background task)
    asyncio.create_task(ai_respond_to_message(message))
    
    return TwiMLResponse("")
```

**4. Opt-in/Opt-out**

- **Opt-in**: User sends keyword "JOIN" to chatroom number
- **Opt-out**: User sends "STOP" → update `opt_in_status` to 'opted_out'
- **Consent logging**: Store timestamp in `consented_at` field
- **Compliance**: TCPA and GDPR consent requirements

**5. Delivery and Retries**

- **Delivery receipts**: Twilio webhook for message status
- **Retry logic**: Exponential backoff for failed sends (3 attempts)
- **Error handling**: Log failures, notify user via WebSocket if SMS fails

**6. Persona Behavior via SMS**

- AI personas respond to SMS messages using same orchestration layer
- Responses sent via Twilio API with `From` number mapped to chatroom
- Short replies critical for SMS (160 chars max, or MMS if longer)

---

## Deployment

### Docker Setup

**Dockerfile** (create in project root):

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

**docker-compose.yml**:

```yaml
version: '3.8'

services:
  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: chatdb
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data

  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql+psycopg2://user:password@db:5432/chatdb
      REDIS_URL: redis://redis:6379/0
      OPENAI_API_KEY: ${OPENAI_API_KEY}
      AUTH_SECRET: ${AUTH_SECRET}
    depends_on:
      - db
      - redis
    volumes:
      - ./:/app
    command: uvicorn app:app --host 0.0.0.0 --port 8000 --reload

volumes:
  postgres_data:
  redis_data:
```

### Environment Variables Reference

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql+psycopg2://user:pass@localhost/chatdb` |
| `REDIS_URL` | Redis connection string | `redis://localhost:6379/0` |
| `OPENAI_API_KEY` | OpenAI API key | `sk-proj-...` |
| `OPENAI_MODEL` | LLM model to use | `gpt-4-turbo-preview` |
| `AUTH_SECRET` | JWT signing secret (min 32 chars) | `your-secret-key-min-32-characters` |
| `JWT_ALGORITHM` | JWT signing algorithm | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiration | `30` |
| `FRONTEND_ORIGIN` | CORS allowed origin | `http://localhost:8000` |
| `ALLOWED_ORIGINS` | Comma-separated CORS origins | `http://localhost:8000,https://app.example.com` |
| `RATE_LIMIT_PER_USER` | Messages per user per minute | `60` |
| `TWILIO_ACCOUNT_SID` | Twilio account SID (Phase 2) | `ACxxxxx` |
| `TWILIO_AUTH_TOKEN` | Twilio auth token (Phase 2) | `your_auth_token` |
| `TWILIO_PHONE_NUMBER` | Twilio phone number (Phase 2) | `+15551234567` |

### Production Deployment

**Run with multiple workers:**

```bash
# Using uvicorn workers
uvicorn app:app --host 0.0.0.0 --port 8000 --workers 4

# Or with gunicorn + uvicorn workers
gunicorn app:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

**Reverse Proxy (Nginx) Example:**

```nginx
server {
    listen 80;
    server_name chat.example.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

**Static File Hosting:**

- **Development**: Serve via FastAPI `FileResponse` (current approach)
- **Production**: Serve assets/ via Nginx or CDN for performance
- **Alternative**: Upload assets to S3/CloudFront and update paths

**Process Management:**

- **Systemd**: Create service file for automatic start/restart
- **Docker Compose**: Use `restart: always` policy
- **Kubernetes**: Deploy with Helm chart (see Next Steps)

---

## Testing and Quality

### Unit Tests

**Test WebSocket Handlers:**

```python
# tests/test_websocket.py
from fastapi.testclient import TestClient
from app import app

def test_websocket_join_leave():
    client = TestClient(app)
    with client.websocket_connect("/chat?user_id=testuser") as ws:
        data = ws.receive_json()
        assert data["event"] == "join"
        assert "testuser" in data["text"]
```

**Test Persona Router:**

```python
# tests/test_ai_router.py
def test_persona_selection_by_mention():
    message = "Hey @einstein, what's relativity?"
    personas = get_active_personas(room_id)
    selected = select_responder(message, personas)
    assert selected.name == "einstein"

def test_turn_taking_policy():
    # Ensure only one AI responds per user message
    last_responder = "einstein"
    selected = select_responder(message, personas, last_responder)
    assert selected.name != last_responder
```

**Test Auth Flows:**

```python
# tests/test_auth.py
def test_signup_success():
    response = client.post("/signup", json={
        "username": "newuser",
        "email": "new@example.com",
        "password": "SecurePass123!"
    })
    assert response.status_code == 201
    assert "access_token" in response.json()

def test_login_invalid_credentials():
    response = client.post("/login", json={
        "username": "user",
        "password": "wrongpassword"
    })
    assert response.status_code == 401
```

### Load Testing

**Locust Script Example:**

```python
# locustfile.py
from locust import HttpUser, task, between
import json

class ChatroomUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        # Login
        response = self.client.post("/login", json={
            "username": f"user_{self.environment.runner.user_count}",
            "password": "password"
        })
        self.token = response.json()["access_token"]
    
    @task(3)
    def send_message(self):
        # Simulate sending a chat message via HTTP endpoint
        self.client.post("/api/rooms/room_1/messages", 
            json={"content": "Hello from load test!"},
            headers={"Authorization": f"Bearer {self.token}"}
        )
    
    @task(1)
    def fetch_messages(self):
        self.client.get("/api/rooms/room_1/messages?limit=20",
            headers={"Authorization": f"Bearer {self.token}"}
        )
```

**Run Load Test:**

```bash
locust -f locustfile.py --host=http://localhost:8000 --users 100 --spawn-rate 10
```

**k6 Alternative:**

```javascript
// k6_test.js
import ws from 'k6/ws';
import { check } from 'k6';

export let options = {
  vus: 50, // 50 concurrent users
  duration: '2m',
};

export default function () {
  const url = 'ws://localhost:8000/chat?user_id=loadtest' + __VU;
  const res = ws.connect(url, function (socket) {
    socket.on('open', () => {
      socket.send('Hello from k6!');
    });
    
    socket.on('message', (data) => {
      check(data, { 'message received': (d) => d.length > 0 });
    });
    
    socket.setTimeout(() => {
      socket.close();
    }, 60000);
  });
}
```

### Linting and Type Checking

**Ruff (linting and formatting):**

```bash
# Install
pip install ruff

# Lint
ruff check .

# Format
ruff format .
```

**Mypy (type checking):**

```bash
# Install
pip install mypy

# Check types
mypy app/ --strict
```

**Pre-commit hooks** (`.pre-commit-config.yaml`):

```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.6
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.7.1
    hooks:
      - id: mypy
        additional_dependencies: [types-all]
```

### CI Pipeline (GitHub Actions)

**.github/workflows/ci.yml**:

```yaml
name: CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_DB: testdb
          POSTGRES_USER: test
          POSTGRES_PASSWORD: test
        ports:
          - 5432:5432
    
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-asyncio pytest-cov
      
      - name: Lint with ruff
        run: ruff check .
      
      - name: Type check with mypy
        run: mypy app/ --strict
      
      - name: Run tests
        env:
          DATABASE_URL: postgresql+psycopg2://test:test@localhost:5432/testdb
        run: pytest --cov=app --cov-report=xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

---

## Next Steps for the AI Agent

This roadmap is prioritized for enterprise readiness. Tackle items in order to build a secure, scalable, production-ready chatroom.

### 1. Wire Database into Chat Flow ⭐ **Critical**

**Goal**: Persist users, rooms, and messages; migrate from in-memory registry to DB-backed presence.

**Tasks**:
- Modify `app.py` to store User records on first connection
- Persist all messages to `messages` table with chatroom_id, user_id, timestamp
- Load last 50 messages from DB when user joins a room
- Implement Redis pub/sub for cross-instance message broadcasting (multi-server support)
- Add `Membership` table checks to enforce room access

**Files to modify**:
- `app.py`: Replace in-memory `clients` dict with DB queries
- `app/models.py`: Add `Message` model
- Create Alembic migration for new tables

---

### 2. Implement Authentication Module ⭐ **Critical**

**Goal**: Secure signup/login/logout with JWT cookies, password hashing, and WebSocket auth.

**Tasks**:
- Create `app/auth.py` with signup, login, logout endpoints
- Use `passlib[bcrypt]` for password hashing
- Generate JWT access/refresh tokens with `python-jose`
- Add `get_current_user` dependency for endpoint protection
- Validate JWT in WebSocket handshake (cookie or query param)
- Implement CSRF token generation for forms

**New files**:
- `app/auth.py`: Auth endpoints and dependencies
- `app/security.py`: Password hashing, JWT utils

---

### 3. Define Persona and Theme Models

**Goal**: CRUD endpoints for managing AI personalities and chatroom themes.

**Tasks**:
- Create `Persona` and `Theme` models in `app/models.py`
- Add migration for new tables
- Implement REST API:
  - `GET /api/personas` (list all personas)
  - `POST /api/personas` (admin-only, create persona)
  - `GET /api/rooms/{room_id}/theme` (get theme)
  - `PUT /api/rooms/{room_id}/theme` (update theme, room admin only)
- Seed default personas (Einstein, Shakespeare, Curie, etc.) via migration or script

**Files to create/modify**:
- `app/models.py`: Add Persona, Theme models
- `app/routers/personas.py`: CRUD endpoints
- `app/routers/themes.py`: Theme management
- `scripts/seed_personas.py`: Default persona seeding

---

### 4. Implement AI Orchestration Service Layer ⭐ **High Priority**

**Goal**: Integrate OpenAI SDK with persona prompts, theme injection, and short-reply constraints.

**Tasks**:
- Create `app/services/ai_orchestrator.py`:
  - `select_responder(message, personas)`: Choose AI based on mentions or relevance
  - `generate_response(persona, context, theme)`: Call OpenAI API with constraints
  - `enforce_short_reply(response)`: Truncate to max_tokens
- Create `app/services/llm_provider.py`: Abstract OpenAI API (support pluggable providers)
- Implement turn-taking policy (only one AI per user message)
- Add async task queue (Celery or asyncio) for AI response generation

**Dependencies**:
- `openai>=1.3.0` SDK
- `tiktoken` for token counting

---

### 5. Add Message Moderation and Safety Filters

**Goal**: Input/output filtering, PII redaction, configurable rate limits.

**Tasks**:
- Create `app/services/moderator.py`:
  - `filter_input(message)`: Block profanity, hate speech (regex + profanity-check lib)
  - `filter_output(ai_response)`: Scan AI replies before sending
  - `redact_pii(text)`: Remove emails, phone numbers, SSNs (regex-based)
- Implement rate limiting with `slowapi` or Redis-based rate limiter
- Log all filtered messages with reason code
- Add user report endpoint: `POST /api/messages/{id}/report`

**Dependencies**:
- `profanity-check` or `better-profanity`
- `slowapi` for rate limiting
- `presidio` (optional, advanced PII detection)

---

### 6. Implement Multi-Room Support

**Goal**: Server-enforced room scoping; users can join multiple rooms with membership checks.

**Tasks**:
- Update WebSocket endpoint to accept room_id: `/chat?room_id={id}&user_id={username}`
- Check `Membership` table before allowing user into room
- Maintain separate `room_queues` per room (Redis pub/sub channels)
- Add REST endpoints:
  - `GET /api/rooms` (list joinable rooms)
  - `POST /api/rooms/{id}/join` (join room, create Membership)
  - `DELETE /api/rooms/{id}/leave` (leave room)

**Files to modify**:
- `app.py`: Multi-room queue management
- `app/models.py`: Membership enforcement

---

### 7. Frontend Chat UI Improvements

**Goal**: Room list, persona picker, theme selector, message threading, typing indicators.

**Tasks**:
- Add room list sidebar to `assets/index.html`
- Implement persona picker (checkboxes for active personas)
- Add theme input field (user can set/update theme)
- Show typing indicators (send `typing` event via WebSocket)
- Display message timestamps and user avatars
- Add "reply to" threading (quote parent message)

**Files to modify**:
- `assets/index.html`: Enhance UI components
- Add JavaScript for persona/theme management

---

### 8. Observability: Logging, Tracing, Metrics

**Goal**: Structured logging, request tracing, Prometheus metrics, error monitoring.

**Tasks**:
- Replace `logging` with `structlog` for JSON logs
- Add `opentelemetry` instrumentation for request tracing
- Expose Prometheus metrics endpoint: `/metrics`
  - Track: requests per endpoint, WebSocket connections, AI response latency, message count
- Integrate Sentry for error monitoring
- Add health check endpoint: `GET /health`

**Dependencies**:
- `structlog`
- `opentelemetry-api`, `opentelemetry-sdk`
- `prometheus-client`
- `sentry-sdk`

---

### 9. Production Configs: Docker, Helm, Secrets

**Goal**: Production-ready Dockerfiles, Helm chart, environment variable documentation.

**Tasks**:
- Create multi-stage Dockerfile (build + runtime stages)
- Add `docker-compose.yml` for local multi-service setup
- Create Kubernetes Helm chart:
  - Deployment, Service, Ingress, ConfigMap, Secret manifests
  - HPA (Horizontal Pod Autoscaler) for auto-scaling
- Document all environment variables in `.env.example`
- Use secrets management (Vault, AWS Secrets Manager, or K8s Secrets)

**Files to create**:
- `Dockerfile`, `docker-compose.yml`
- `helm/chatroom/` chart directory
- `.env.example`

---

### 10. Phase 2 SMS: Twilio Integration

**Goal**: SMS webhook endpoints, phone verification, user-to-SMS mapping, background delivery tasks.

**Tasks**:
- Create `app/routers/sms.py`:
  - `POST /sms/incoming`: Twilio webhook for inbound SMS
  - `POST /sms/verify`: Send verification code to phone
  - `POST /sms/confirm`: Confirm verification code
- Add `PhoneNumber` model with opt-in status
- Implement Twilio API client (`twilio` SDK)
- Create background task for sending AI responses via SMS (Celery or asyncio)
- Handle delivery receipts: `POST /sms/status` (Twilio webhook)

**Dependencies**:
- `twilio` SDK

---

### 11. Security Hardening

**Goal**: OWASP ASVS alignment, dependency scanning, security headers, CORS hardening.

**Tasks**:
- Run `safety check` for vulnerable dependencies
- Add `bandit` for security linting
- Implement security headers middleware (CSP, HSTS, X-Frame-Options)
- Harden CORS: specific origins, credentials support
- Enable secret scanning in CI (GitHub secret scanning, `truffleHog`)
- Add input validation with Pydantic models for all endpoints
- Implement SQL injection protection (SQLAlchemy parameterized queries)

**Dependencies**:
- `safety`, `bandit`
- `secure` (security headers middleware)

---

### 12. Performance and Scale

**Goal**: Redis pub/sub, horizontal scaling, backpressure handling.

**Tasks**:
- Replace in-memory `room_queue` with Redis pub/sub channels (one per room)
- Implement connection pooling for DB and Redis
- Add WebSocket backpressure handling (drop messages if client can't keep up)
- Document horizontal scaling:
  - Multiple FastAPI instances behind load balancer
  - Sticky sessions not required (JWT stateless auth)
  - Redis for shared state
- Add caching layer (Redis) for frequently accessed data (personas, themes)

**Dependencies**:
- `redis[hiredis]` for high-performance Redis client

---

### 13. End-to-End and CI Testing

**Goal**: E2E tests for WebSocket flows; CI pipeline with lint/type/test.

**Tasks**:
- Create `tests/e2e/test_chatroom_flow.py`:
  - Test full user journey: signup → login → join room → send message → AI responds
  - Test WebSocket message broadcast to multiple clients
- Set up CI pipeline (GitHub Actions, GitLab CI):
  - Lint (ruff), type check (mypy), test (pytest), coverage (codecov)
  - Run tests on PR and main branch
  - Block merge if tests fail
- Add load tests to CI (run k6 or locust in CI for performance regression)

**Files to create**:
- `tests/e2e/`
- `.github/workflows/ci.yml` (if using GitHub Actions)

---

## License

See [LICENSE](LICENSE) file for details.

---

## Contributing

Contributions are welcome! Please open an issue or pull request with your proposed changes.

**Development Workflow:**
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature-name`
3. Make changes and add tests
4. Run linters and tests: `ruff check . && pytest`
5. Commit with descriptive messages: `git commit -m "feat: add persona selection"`
6. Push and open a pull request

---

## Support

For questions or issues, please open a GitHub issue or contact the maintainers.

---

**Last Updated**: 2024-01-15  
**Version**: 0.1.0 (MVP in progress)
