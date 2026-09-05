# Digi-Chalk / Samarthya — Frontend Handoff Guide

This document exists so a backend developer can pick up the frontend and know exactly what data each screen expects, without needing to read every line of HTML/JS to figure it out.

---

## 1. What "frontend-only" means here

Every screen currently renders with **static placeholder values written directly into the markup** — no separate fake-data layer, no dummy JSON files sitting in the repo pretending to be an API. Each placeholder is clearly flagged (see Section 3) so it's obvious at a glance what needs to be wired up once the backend exists.

---

## 2. Folder structure (as built)

```
project/
├── index/
│   ├── index.html              # role-based login / landing
│   ├── teacher.html
│   ├── student.html
│   ├── parent.html
│   ├── headmaster.html
│   ├── quiz.html                # AI quiz flow (linked from student.html)
│   ├── replay.html              # whiteboard replay timeline (linked from student.html)
│   └── board.html               # fullscreen landscape live board, shared by
│                                 # teacher ("Open full board") and student ("Join")
│                                 # via ?role=teacher|student
├── templates/
│   ├── style.css                # global design tokens + shared styles
│   ├── script.js                # shared logic (skeleton loading, nav, toggles, utils)
│   └── components/
│       ├── live-board.js        # canvas stroke rendering, session start, bookmarking
│       ├── quiz.js              # one-question-at-a-time quiz flow
│       ├── condenser.js         # recap reel playback
│       └── scores.js            # score bars + admin class list/sort
├── assets/
│   ├── icons/                   # empty — all icons are currently inline SVG
│   └── fonts/                   # empty — Plus Jakarta Sans is loaded from Google Fonts
│                                 # (see Section 7, "Fonts")
└── HANDOFF.md                    # this file

smoketest.js, interaction-test.js  # Playwright test scripts used to verify this build
                                     # (not part of the shipped app — safe to delete,
                                     # or keep in CI if useful)
```

`quiz.html`, `replay.html`, and `board.html` weren't in the original 5-file sketch but were added because the data contract in Section 4 already implies them (`Student.quiz.*`, `Student.replay.*`, and the live board itself all need a dedicated screen to make sense of those fields).

Splitting JS into `components/` (one file per feature) makes it much easier for the backend dev to work on one integration at a time instead of untangling a single giant `script.js`.

---

## 3. Mark every integration point in the code itself

This is the part that replaces mock data entirely — instead of a fake API response sitting in a file, the exact spot needing real data is flagged right where it lives in the code, using a consistent tag:

```html
<!-- INTEGRATION: class average score — replace with GET /api/scores/{classId} -->
<span>78%</span>
```

```js
// INTEGRATION: class list for this school — replace with GET /api/schools/{schoolId}/classes
// Expected shape: see Section 4, "Headmaster"
function loadClasses() { ... }
```

A quick `grep -rn "INTEGRATION" .` from the project root surfaces every single place that needs touching. Every static demo array (`CLASS_DEMO`, `QUIZ_DEMO`, `STROKE_DEMO`, `RECAP_DEMO`) sits directly above its own INTEGRATION comment in the relevant `components/*.js` file.

---

## 4. Data contracts per portal

These are schemas, not sample data — field names and types only. Treat this as the first draft of the real API contract, and confirm it with your backend dev before they start building.

### Teacher
```
session.status          string   ("idle" | "recording" | "ended")
session.classId         string
session.elapsedSeconds  number
board.strokes[]         array of { x: number, y: number, dt: number, color: string }
bookmarks[]             array of { timestamp: number, label: string }
scores.unit             string
scores.classAverage     number
scores.submittedCount   number
```
> Note: the `{x, y, dt}` stroke format matches the vector telemetry format already defined in your product doc — keep it consistent so the hardware/board team doesn't need a translation layer.

### Student
```
classes[]                string[]
liveSession.isLive       boolean
liveSession.classId      string
replay.lessonId          string
replay.progress          number   (0–1)
replay.bookmarks[]       number[] (0–1 positions on the timeline)
audioEnabled             boolean
quiz.available           boolean
quiz.sourceLessonId      string
recaps[]                 array of { id: string, durationSec: number, url: string }
```

### Parent
```
children[]                array of { id: string, name: string }
activeChildId              string
notification.channel       string   ("whatsapp" | "sms")
notification.text          string
summary.language           string   (ISO code, e.g. "ta")
summary.text                string
weekly.averageScore         number
weekly.lessonsWatched       number
weekly.lessonsTotal         number
```

### Headmaster
```
school.name             string
school.avgScore         number
school.avgInteraction   number
classes[]                array of { id: string, avgScore: number, interaction: number, flag: string | null }
sort                    string   ("score-asc" | "score-desc" | ...)
```
No teacher-level fields anywhere in this contract — worth double-checking with your backend dev that the API mirrors this, since it's easy for a backend query to accidentally join in teacher data even if the frontend never displays it. The admin screen was tested to confirm no teacher name or identifier renders anywhere in its markup.

---

## 5. Hardware & real-time notes for the backend dev

- **Live board strokes** — needs a persistent connection (WebSocket is the common choice) streaming stroke events in the `{x, y, dt}` shape above. The frontend currently renders a static demo path (`STROKE_DEMO` in `live-board.js`) as a stand-in for this feed, on both the teacher's live window and `board.html`.
- **BLE/UDP pairing** — happens device-side, outside the frontend's control. The frontend's "Start session" button (`initSessionButton` in `live-board.js`) just needs one endpoint/event to call, and one thing back: a session ID, a connection-status flag, or both.
- **Video/audio (recordings, replay, condensed reels)** — frontend assumes it will receive a URL or stream reference once available. Confirm MP4 file URL vs. HLS stream early, since it changes how the playback element gets wired up in `condenser.js` and `replay.html`.
- **SMS/WhatsApp + regional translation** — entirely backend-triggered; the frontend doesn't send anything, it just renders whatever notification history/summary text comes back.
- **Forced landscape on `board.html`** — the Screen Orientation API's `lock()` only works reliably inside fullscreen on most mobile browsers, so `tryLockLandscape()` in `live-board.js` is a best-effort progressive enhancement. The real fallback that always works is a CSS media query (`.board-page .rotate-guard`, in `style.css`) that shows a "rotate your device" prompt and hides the board entirely while the viewport is in portrait. Tested in both orientations.

---

## 6. Fonts

`Plus Jakarta Sans` is loaded via Google Fonts (`<link>` in every page's `<head>`). The CSS fallback stack is `"Plus Jakarta Sans", "Inter", system-ui, -apple-system, "Segoe UI", sans-serif`, so the app still looks correct — just with a system font — on a first load with no connectivity, which matters given the low-bandwidth target audience. If you'd rather self-host the font (recommended for production, one less external request), drop the woff2 files in `assets/fonts/` and swap the `<link>` for a local `@font-face` block in `style.css`.

---

## 7. Design tokens

All colors, spacing, radii, shadows, and type sizes are CSS custom properties at the top of `templates/style.css` — change a value there and it updates everywhere. Score/engagement color bands (green ≥75, amber 60–74, red <60) are centralized in one function, `classifyValue()` in `script.js`, and every score bar, badge, and card border derives its color from it — so there's no risk of a bar and its badge disagreeing on a class's status.

---

## 8. What's been tested

- `node --check` on every JS file (syntax)
- W3C/Nu HTML validator on every page (markup)
- All internal `href`/`src` links resolve to real files
- Real headless-Chromium run of all 9 pages with no console or page errors
- Scripted interaction tests: session start/timer, bookmarking, subject-chip selection, low-bandwidth toggle, quiz validation + scoring, recap playback, parent child-switcher, admin sort-by-lowest, and the landscape guard on `board.html` in both orientations and both roles

Two real bugs were caught and fixed this way before handoff: a CSS specificity issue that stretched the admin rollup card's divider line into a solid block, and a mismatched color-threshold between a class's score bar and its flag badge. Worth keeping an eye out for the same class of bug (a CSS rule matching more elements than intended) if you extend the stylesheet.

---

## 9. How to run locally

No build step. From the `project/` folder:

```
npx live-server index
```

or simply open `index/index.html` directly in a browser. Every page also works opened standalone (e.g. `index/teacher.html`) without going through the landing page first.

---

## 10. Handoff checklist

- [x] Every placeholder value in the markup is flagged with an `INTEGRATION` comment — none left silently hardcoded
- [x] Each screen's expected data shape matches the schema in Section 4
- [x] Consistent naming: kebab-case for HTML ids/classes, camelCase for JS variables/JSON keys
- [x] "How to run locally" note — see Section 9
- [ ] Repo shared with a clear branch (e.g. `frontend-v1`) so backend work doesn't collide with ongoing frontend changes — do this when you push

---

## 11. One communication tip

Before the backend dev writes a single endpoint, sit down (or share this doc async) and get explicit agreement that the schemas in Section 4 *are* the API contract, not just a placeholder guess. It's far cheaper to renegotiate a field name now than after both sides have built against different assumptions.
