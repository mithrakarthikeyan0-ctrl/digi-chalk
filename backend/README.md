# Digi-Chalk Backend

This is the secure cloud-backend foundation for the Digi-Chalk platform, built with Python and Django REST Framework.

## Features
- Custom JWT Authentication (email-based)
- Role-based Access Control (Teacher, Student, Parent, Headmaster, Admin)
- PostgreSQL for production, SQLite for local development
- OpenAPI 3 (Swagger) documentation

## Setup Instructions (Windows PowerShell)

### 1. Create Virtual Environment
```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 2. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 3. Environment Variables
Copy `.env.example` to `.env`. This step is crucial even for local development.
```powershell
Copy-Item .env.example -Destination .env
```
Ensure you have `DJANGO_SECRET_KEY` set.

### 4. Database Setup (Local SQLite)
For local development, SQLite is used by default if no `DATABASE_URL` is provided.
```powershell
python manage.py makemigrations
python manage.py migrate
```

### 5. Running the Server (ASGI/WebSockets)
```powershell
daphne config.asgi:application
```
The server will start at `http://127.0.0.1:8000/`. (Note: `python manage.py runserver` also works for local development as it now routes through Daphne).

### 6. Running Tests
Tests are written using `pytest`.
```powershell
pytest
```

### 7. Running the Frontend
```powershell
# Open a new terminal in the repository root (outside backend folder)
npx live-server index
```

## API Contract (Phase 1 & 2)

These endpoints are designed to integrate with the static frontend placeholders:

| Endpoint | Method | Role | Frontend File / Feature |
| --- | --- | --- | --- |
| `/api/v1/health/` | GET | Any | Server Health |
| `/api/v1/auth/login/` | POST | Any | `index.html` (Login) |
| `/api/v1/auth/me/` | GET | Auth | Load user profile / role data |
| `/api/v1/classes/` | GET | Student/Parent | `student.html`, `parent.html` class lists |
| `/api/v1/sessions/` | GET/POST | Teacher/Student | `live-board.js` / session start |
| `/api/v1/sessions/{id}/end/` | POST | Teacher | `live-board.js` / session end |
| `/api/v1/sessions/{id}/bookmarks/` | GET/POST | Teacher | `live-board.js` / bookmarking |
| `ws://127.0.0.1:8000/ws/sessions/{id}/board/` | WS | Auth | `board.html` / Live Board WebSockets |

### Live Board WebSocket Event Contract
The WebSocket uses an initial JSON message for authentication instead of URL query parameters.
**Client Authentication:**
`{"type": "authenticate", "token": "JWT_ACCESS_TOKEN"}`

**Teacher Strokes (Broadcast):**
`{"type": "stroke", "strokeId": "uuid", "points": [{"x": 10.5, "y": 20.0, "dt": 0.0, "color": "#ffffff"}]}`

## Docker / PostgreSQL / Redis Setup (Production)

To run the backend with a PostgreSQL database and Redis for Channels in Docker:
```powershell
docker-compose up --build
```
Ensure your `.env` contains:
`DATABASE_URL=postgres://postgres:postgres@db:5432/digichalk`
`REDIS_URL=redis://redis:6379/0`

*Note: For local development, an `InMemoryChannelLayer` is used by default if `REDIS_URL` is not set.*
*Note: Phase 2 only keeps the current in-memory board state for demo purposes without persisting every stroke to PostgreSQL.*
