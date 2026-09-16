# Digi-Chalk

Low-bandwidth classroom learning and collaborative whiteboard frontend designed for resource-constrained education environments.

> **Note**: This repository contains the **frontend prototype only** and currently runs entirely on client-side demo data and static simulations. No real backend, hardware peripherals, or external AI services are currently connected.

---

## Overview

Digi-Chalk (Samarthya) bridges classroom chalkboards and student devices over low-bandwidth connections (such as 2G/EDGE networks). The interface prioritizes lightweight vector stroke telemetry over heavy video streaming, ensuring that students, teachers, parents, and school administrators can stay connected and informed even in rural or connectivity-challenged environments.

### Implemented Portals
- **Teacher Portal (`/teacher`)**: Live chalkboard session broadcasting, real-time classroom timer, interactive bookmarking of key explanations, and student score rollups.
- **Student Portal (`/student`)**: Subject filtering (Maths, Science, English, Social Studies), live session status card with "Join live board" action, low-bandwidth data saving mode, 30-second lecture condenser reels, and direct access to chapter replays and quizzes.
- **Parent Portal (`/parent`)**: Multi-child switcher, multilingual daily learning digests (English and Tamil), score breakdowns, and delivery logs for SMS/WhatsApp notices.
- **Headmaster Portal (`/headmaster`)**: School-wide performance rollups, class sortability (by score or interaction level), engagement tracking, and attention flags.
- **Live Board (`/board`)**: Fullscreen landscape chalkboard view shared by teachers and students via `?role=teacher` or `?role=student`, featuring orientation protection and chalk drawing simulation.
- **AI Quiz Flow (`/quiz`)**: Single-question assessment flow with step progress indicators, selection validation, score tallying (`n / 3`), performance breakdown, and retake capability.
- **Whiteboard Replay (`/replay`)**: Synced stroke replay with interactive playhead scrubbing, keyboard timeline navigation, teacher bookmark quick-jump points, and low-data modes.

---

## Key Features

- **Chalkboard Vector Telemetry**: Lightweight stroke rendering using HTML5 Canvas instead of high-bandwidth video streams.
- **Teacher Bookmarking**: Mark important teaching moments during class to let students jump straight to critical notes.
- **Lecture Condenser**: 30-second condensed video/stroke review reels for rapid chapter revision.
- **Interactive AI Quiz Flow**: Question-by-question self-assessment with instant feedback, explanation breakdown, and score summary.
- **Low-Bandwidth Mode**: Toggleable data-saving mode that mutes audio and prioritizes low-overhead SVG/canvas vector paths.
- **Mobile-First Responsive Design**: Designed with a constructivist paper aesthetic, tested down to 360px viewports with `:focus-visible` keyboard accessibility and ARIA semantics.

---

## Technology Stack

- **Framework**: React with Vite
- **Routing**: React Router
- **State Management**: React Context (`AppContext`)
- **Styling**: Modular CSS (`tokens.css`, `globals.css`)
- **Graphics**: HTML5 Canvas API for vector stroke rendering
- **Testing**: Vitest for unit testing

---

## Folder Structure

```
Digi_Chalk/
├── frontend/
│   ├── public/                 # Static assets
│   ├── src/
│   │   ├── components/         # Reusable UI Atoms and Layouts
│   │   ├── context/            # Global State Management
│   │   ├── data/               # Mock Demo Data
│   │   ├── pages/              # Role Portals and Features
│   │   ├── styles/             # Global and Modular CSS
│   │   ├── App.jsx             # React Router setup
│   │   └── main.jsx            # Entry point
│   ├── vite.config.js          # Vite configuration
│   └── package.json            # Dependencies
├── legacy-static/              # Old static HTML/JS frontend
├── backend/                    # Django Cloud Backend
├── gateway/                    # FastAPI Classroom Gateway
├── HANDOFF.md                  # Backend handoff guide & data contracts
└── README.md                   # Repository documentation
```

---

## Local Setup

Navigate to the `frontend/` directory, install dependencies, and run the development server:

```bash
cd frontend
npm install
npm run dev
```

Then open `http://localhost:5173` in your browser.

---

## Testing

Automated verification is built with Vitest:

- Run tests:
```bash
cd frontend
npm run test
```

- Run build:
```bash
npm run build
```

---

## System Architecture

Digi-Chalk consists of three primary components:
1. **Frontend (HTML/JS/CSS)**: The static web UI, functioning strictly on the client.
2. **Cloud Backend (Django)**: REST APIs, real-time WebSocket sessions, Early Warning Systems (EWS), quizzes, attendance, and notification dispatching.
3. **Gateway (FastAPI)**: Local classroom edge server handling hardware synchronization and offline operation for low-bandwidth schools.

---

## Local Development (Docker Compose)

The easiest way to run the full stack locally is with Docker Compose.

### 1. Environment Setup
Copy the example environment files:
```bash
cp backend/.env.example backend/.env
cp gateway/.env.example gateway/.env
```

### 2. Start Services
Run the entire stack in the background:
```bash
docker-compose up -d --build
```
This starts PostgreSQL, Redis, Backend, Gateway, and a static file server for the frontend.

### 3. Seed Demo Data
The backend requires a baseline database state. Run the safe seed script to populate a demo school, users, classes, and dummy content:
```bash
docker-compose exec backend python manage.py seed_demo_data
```

### 4. Accessing the Application
- **Frontend**: http://localhost:5173/index/index.html
- **Backend API Docs**: http://localhost:8000/api/v1/docs/
- **Gateway Status**: http://localhost:8001/status/

*Local Frontend Fallback without Docker*: Run `npx live-server . --port=5173` in the repository root.

---

## Testing & CI

Continuous Integration is managed via GitHub Actions. We run Python `pytest` suites and `ruff` linting on both the backend and gateway services.

### Running Backend Tests Locally
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # or .\.venv\Scripts\Activate.ps1 on Windows
pip install -r requirements.txt
pytest
```

---

## Production Deployment Guide

### Deployment Checklist

- **Secrets**: Provide secure, random `DJANGO_SECRET_KEY` and `GATEWAY_API_KEY`. DO NOT commit these to version control.
- **HTTPS**: Run the backend and frontend behind an HTTPS reverse proxy (e.g. Nginx, Traefik, AWS ALB). Enable `SECURE_SSL_REDIRECT`, `SESSION_COOKIE_SECURE`, and `CSRF_COOKIE_SECURE` environment variables.
- **CORS & Allowed Hosts**: Strictly set `DJANGO_ALLOWED_HOSTS`, `CORS_ALLOWED_ORIGINS`, and `CSRF_TRUSTED_ORIGINS` to the exact production domains.
- **Database Backup**: Configure automated snapshotting for the PostgreSQL instance. (A local manual backup script is provided at `scripts/backup_db.sh`).
- **Channel Layer**: Point `REDIS_URL` to a persistent Redis instance for WebSocket routing.

### Data Privacy & Security Limitations
- **Notifications**: Real providers (SMS/WhatsApp) are disabled by default. Do not enable production credentials unless strict legal data handling consent forms are signed by the school.
- **Early Warning System (EWS)**: The current models act as proof-of-concept baselines using generic indicators. **Do not use automated output for disciplinary or labeling actions without human review.** EWS must remain strictly as an internal alert pipeline for teachers.

---

Consult [HANDOFF.md](HANDOFF.md) for the data schema and hardware specifications.
