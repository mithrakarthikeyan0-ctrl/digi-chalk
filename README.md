# Digi-Chalk

Low-bandwidth classroom learning and collaborative whiteboard frontend designed for resource-constrained education environments.

> **Note**: This repository contains the **frontend prototype only** and currently runs entirely on client-side demo data and static simulations. No real backend, hardware peripherals, or external AI services are currently connected.

---

## Overview

Digi-Chalk (Samarthya) bridges classroom chalkboards and student devices over low-bandwidth connections (such as 2G/EDGE networks). The interface prioritizes lightweight vector stroke telemetry over heavy video streaming, ensuring that students, teachers, parents, and school administrators can stay connected and informed even in rural or connectivity-challenged environments.

### Implemented Portals
- **Teacher Portal (`index/teacher.html`)**: Live chalkboard session broadcasting, real-time classroom timer, interactive bookmarking of key explanations, and student score rollups.
- **Student Portal (`index/student.html`)**: Subject filtering (Maths, Science, English, Social Studies), live session status card with "Join live board" action, low-bandwidth data saving mode, 30-second lecture condenser reels, and direct access to chapter replays and quizzes.
- **Parent Portal (`index/parent.html`)**: Multi-child switcher, multilingual daily learning digests (English and Tamil), score breakdowns, and delivery logs for SMS/WhatsApp notices.
- **Headmaster Portal (`index/headmaster.html`)**: School-wide performance rollups, class sortability (by score or interaction level), engagement tracking, and attention flags.
- **Live Board (`index/board.html`)**: Fullscreen landscape chalkboard view shared by teachers and students via `?role=teacher` or `?role=student`, featuring orientation protection and chalk drawing simulation.
- **AI Quiz Flow (`index/quiz.html`)**: Single-question assessment flow with step progress indicators, selection validation, score tallying (`n / 3`), performance breakdown, and retake capability.
- **Whiteboard Replay (`index/replay.html`)**: Synced stroke replay with interactive playhead scrubbing, keyboard timeline navigation, teacher bookmark quick-jump points, and low-data modes.

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

- **Structure**: Semantic HTML5
- **Styling**: Vanilla CSS (design tokens, paper texture system, mobile-first responsive layout, no external CSS frameworks)
- **Logic**: Vanilla JavaScript (ES6+, zero frontend frameworks, component-based structure)
- **Graphics**: HTML5 Canvas API for vector stroke rendering
- **Testing**: Playwright for end-to-end smoke and interaction verification

---

## Folder Structure

```
Digi_Chalk/
├── assets/
│   ├── fonts/                  # Font assets (Plus Jakarta Sans fallback stack)
│   └── icons/                  # SVG icons and visual symbols
├── index/
│   ├── index.html              # Role selection & login landing page
│   ├── teacher.html            # Teacher session & board controls
│   ├── student.html            # Student dashboard & subject lessons
│   ├── parent.html             # Parent multi-child learning digests
│   ├── headmaster.html         # Headmaster school analytics & class ranking
│   ├── board.html              # Fullscreen landscape live chalkboard view
│   ├── quiz.html               # One-question-at-a-time AI quiz flow
│   └── replay.html             # Synced whiteboard replay with bookmarks
├── templates/
│   ├── style.css               # Design tokens, color system, and shared styles
│   ├── script.js               # Shared logic (modals, loaders, switches, announcer)
│   └── components/
│       ├── live-board.js       # Chalkboard canvas stroke rendering & session state
│       ├── quiz.js             # Quiz progression, validation, scoring, and retake
│       ├── condenser.js        # 30-second lecture condenser playback & completion
│       └── scores.js           # Score classifying, bars, and admin class sorting
├── test-runner.js              # Playwright cross-browser interaction test runner
├── smoketest.js                # Playwright smoke test script
├── interaction-test.js         # Playwright interaction test script
├── HANDOFF.md                  # Comprehensive backend handoff guide & data contracts
├── .gitignore                  # Git hygiene ignore rules
└── README.md                   # Repository documentation
```

---

## Local Setup

No build step or compilation required. Run locally using any static web server:

```bash
# Using live-server (recommended)
npx live-server index --port=5173

# Or using Python's built-in HTTP server
python -m http.server 5173
```

Then open `http://localhost:5173/index/index.html` in your browser. Every page can also be opened standalone (e.g. `index/student.html`).

---

## Testing

Automated verification is built with Playwright:

- **`test-runner.js` / `interaction-test.js`**: Verifies teacher session start/timer, bookmarking, student subject chips, low-bandwidth toggle, condenser playback progress, quiz validation and scoring (`n / 3`), parent child switcher, admin sorting, board landscape guard, and replay bookmark jump.
- **`smoketest.js`**: Verifies that all 9 portal pages load cleanly without uncaught console errors or 404 resource failures.

To run tests:
```bash
node test-runner.js
```

*Note*: Ensure a local server is running at port `8123` (or the configured `BASE` URL) prior to running tests. On Windows environments, Edge or Chromium is used as the browser channel.

---

## Future Backend Integration Areas

All placeholder mock data in the code is explicitly flagged with `INTEGRATION` comments for streamlined backend wiring. Key integration areas include:

1. **Authentication & Session Management**: Role-based authentication (`teacher`, `student`, `parent`, `headmaster`) and session tokens.
2. **REST API Endpoints**:
   - `GET /api/students/{id}/classes` — Student enrolled subjects and lesson progress.
   - `GET /api/lessons/{id}` — Lesson metadata, board strokes, duration, and bookmarks.
   - `GET /api/quiz/{lessonId}` & `POST /api/quiz/{lessonId}/attempts` — Quiz questions and student attempt score submissions.
   - `GET /api/schools/{schoolId}/classes` — School performance metrics for headmaster portal.
   - `GET /api/parents/{id}/children` — Multilingual summaries and attendance digests.
3. **Live Board WebSockets / SSE**: Real-time vector stroke streaming (`{x, y, dt, color}`) and live session status broadcasts (`Student.liveSession.isLive`).
4. **Media CDN & Adaptive Bitrate**: Low-bandwidth variants (audio-only, compressed audio, or lightweight vector streams) tied to the low-bandwidth switch.
5. **Telemetry & Progress Storage**: Periodic sync of student replay playhead positions (`POST /api/students/{id}/progress`).

Consult [HANDOFF.md](HANDOFF.md) for the complete data schema and hardware specifications.
