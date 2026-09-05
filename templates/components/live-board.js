/* ============================================================
   Live board component
   Used by: teacher.html (record + bookmark), student.html
   (live banner + replay), board.html (fullscreen landscape view)
   ============================================================ */

/**
 * INTEGRATION: replace STROKE_DEMO with the real stream.
 * Expected shape per data contract, Section 4 "Teacher":
 *   board.strokes[] = [{ x: number, y: number, dt: number, color: string }, ...]
 * In production this array is not static — it grows over a
 * WebSocket connection while session.status === "recording".
 * `color` values map to the three chalk tones below.
 */
var STROKE_DEMO = [
  { path: "M20 60 Q 70 30 130 65 T 250 55", color: "#F1F5F9" },
  { path: "M25 110 L 160 110", color: "#FCD34D" },
  { path: "M25 140 Q 90 165 160 135 T 300 145", color: "#6EE7B7" }
];

function drawBoardStrokes(canvas, strokes) {
  if (!canvas || !canvas.getContext) return;
  var ctx = canvas.getContext("2d");
  var ratio = window.devicePixelRatio || 1;
  var cssWidth = canvas.clientWidth || 320;
  var cssHeight = canvas.clientHeight || 170;
  canvas.width = cssWidth * ratio;
  canvas.height = cssHeight * ratio;
  ctx.scale(ratio, ratio);
  ctx.clearRect(0, 0, cssWidth, cssHeight);
  ctx.lineWidth = 2.5;
  ctx.lineCap = "round";
  (strokes || STROKE_DEMO).forEach(function (stroke) {
    var p = new Path2D(stroke.path);
    ctx.strokeStyle = stroke.color;
    ctx.stroke(p);
  });
}

/**
 * Draws strokes progressively up to a percentage (0.0 to 1.0)
 * used by lesson replay timeline scrubbing.
 */
function drawBoardStrokesProgressive(canvas, strokes, progressPct) {
  if (!canvas || !canvas.getContext) return;
  var ctx = canvas.getContext("2d");
  var ratio = window.devicePixelRatio || 1;
  var cssWidth = canvas.clientWidth || 320;
  var cssHeight = canvas.clientHeight || 170;
  canvas.width = cssWidth * ratio;
  canvas.height = cssHeight * ratio;
  ctx.scale(ratio, ratio);
  ctx.clearRect(0, 0, cssWidth, cssHeight);
  ctx.lineWidth = 2.5;
  ctx.lineCap = "round";

  var items = strokes || STROKE_DEMO;
  var totalStrokes = items.length;
  var visibleCount = Math.max(1, Math.ceil(totalStrokes * Math.min(Math.max(progressPct, 0.05), 1.0)));

  for (var i = 0; i < visibleCount && i < totalStrokes; i++) {
    var stroke = items[i];
    var p = new Path2D(stroke.path);
    ctx.strokeStyle = stroke.color;
    ctx.stroke(p);
  }
}

/**
 * Enables interactive teacher chalk drawing on the fullscreen board.
 * Supports touch, pen, and mouse inputs with low latency.
 */
function enableBoardDrawing(canvas, getActiveColor) {
  if (!canvas || !canvas.getContext) return;
  var ctx = canvas.getContext("2d");
  var drawing = false;
  var lastX = 0;
  var lastY = 0;

  function getCanvasCoords(e) {
    var rect = canvas.getBoundingClientRect();
    var clientX = e.touches ? e.touches[0].clientX : e.clientX;
    var clientY = e.touches ? e.touches[0].clientY : e.clientY;
    return {
      x: clientX - rect.left,
      y: clientY - rect.top
    };
  }

  function startDraw(e) {
    e.preventDefault();
    drawing = true;
    var pos = getCanvasCoords(e);
    lastX = pos.x;
    lastY = pos.y;
  }

  function moveDraw(e) {
    if (!drawing) return;
    e.preventDefault();
    var pos = getCanvasCoords(e);
    var color = typeof getActiveColor === "function" ? getActiveColor() : "#F1F5F9";
    
    var ratio = window.devicePixelRatio || 1;
    ctx.save();
    ctx.setTransform(1, 0, 0, 1, 0, 0); // reset scale for direct drawing with ratio
    ctx.beginPath();
    ctx.moveTo(lastX * ratio, lastY * ratio);
    ctx.lineTo(pos.x * ratio, pos.y * ratio);
    ctx.strokeStyle = color;
    ctx.lineWidth = 3 * ratio;
    ctx.lineCap = "round";
    ctx.lineJoin = "round";
    ctx.stroke();
    ctx.restore();

    /* INTEGRATION: emit stroke vector event { x: pos.x, y: pos.y, dt: Date.now(), color: color } to WebSocket */

    lastX = pos.x;
    lastY = pos.y;
  }

  function stopDraw(e) {
    if (!drawing) return;
    drawing = false;
  }

  canvas.addEventListener("mousedown", startDraw);
  canvas.addEventListener("mousemove", moveDraw);
  window.addEventListener("mouseup", stopDraw);

  canvas.addEventListener("touchstart", startDraw, { passive: false });
  canvas.addEventListener("touchmove", moveDraw, { passive: false });
  window.addEventListener("touchend", stopDraw);
}

/**
 * Wires the teacher's single-tap "Start session" button.
 * INTEGRATION: on tap, call the session-start endpoint. It should
 * return { sessionId, status } — swap the setInterval timer below
 * for whatever elapsed-time source the backend provides (server
 * timestamp is safer than a client timer once reconnects happen).
 */
function initSessionButton(buttonEl, timerEl, onStart, onStop) {
  if (!buttonEl) return;
  var recording = false;
  var seconds = 0;
  var intervalId = null;

  buttonEl.addEventListener("click", function () {
    recording = !recording;
    buttonEl.classList.toggle("is-recording", recording);
    var mainLabel = buttonEl.querySelector(".label-main");
    var subLabel = buttonEl.querySelector(".label-sub");

    if (recording) {
      seconds = 0;
      mainLabel.textContent = "Recording…";
      subLabel.textContent = "Tap to end session";
      intervalId = window.setInterval(function () {
        seconds += 1;
        if (timerEl) timerEl.textContent = formatDuration(seconds);
      }, 1000);
      announce("Session started");
      if (typeof onStart === "function") onStart();
    } else {
      window.clearInterval(intervalId);
      mainLabel.textContent = "Start session";
      subLabel.textContent = "One tap to record and broadcast";
      announce("Session ended");
      if (typeof onStop === "function") onStop(seconds);
    }
  });
}

/**
 * Wires the amber bookmark button. Tags the current session
 * timestamp as exam-important.
 * INTEGRATION: POST { timestamp, label } to bookmarks endpoint —
 * see data contract "Teacher.bookmarks[]". The physical chalk
 * holder's double-tap gesture should hit the same endpoint;
 * this button is the on-screen equivalent for parity when the
 * hardware isn't paired.
 */
function initBookmarkButton(buttonEl, timerEl, listEl) {
  if (!buttonEl) return;
  buttonEl.addEventListener("click", function () {
    var stamp = timerEl ? timerEl.textContent : "0:00";
    if (listEl) {
      var item = document.createElement("li");
      item.textContent = "Bookmarked at " + stamp;
      listEl.prepend(item);
    }
    announce("Moment bookmarked at " + stamp);
    buttonEl.animate(
      [{ transform: "scale(1)" }, { transform: "scale(1.15)" }, { transform: "scale(1)" }],
      { duration: 220 }
    );
  });
}

/**
 * Best-effort landscape lock for the dedicated board page.
 * The Screen Orientation API only grants lock in fullscreen on most
 * mobile browsers, so this is a progressive enhancement — the CSS
 * rotate-guard in style.css is the real fallback and always works.
 */
function tryLockLandscape() {
  try {
    if (screen.orientation && screen.orientation.lock) {
      screen.orientation.lock("landscape").catch(function () {});
    }
  } catch (e) {
    /* orientation lock unsupported — CSS rotate-guard handles it */
  }
}

document.addEventListener("DOMContentLoaded", function () {
  document.querySelectorAll("[data-board-canvas]").forEach(function (canvas) {
    drawBoardStrokes(canvas, STROKE_DEMO);
    window.addEventListener("resize", function () { drawBoardStrokes(canvas, STROKE_DEMO); });
  });
});
