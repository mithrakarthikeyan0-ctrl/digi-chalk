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
  ctx.lineJoin = "round";
  (strokes || STROKE_DEMO).forEach(function (stroke) {
    var p = new Path2D(stroke.path);
    ctx.strokeStyle = stroke.color;
    ctx.stroke(p);
  });
}

/**
 * Animates strokes for a realistic demo live-board experience.
 */
function animateBoardStrokes(canvas, strokes, durationMs = 3000) {
  if (!canvas || !canvas.getContext) return;
  var items = strokes || STROKE_DEMO;
  var startTime = null;

  function step(timestamp) {
    if (!startTime) startTime = timestamp;
    var progress = Math.min((timestamp - startTime) / durationMs, 1.0);
    drawBoardStrokesProgressive(canvas, items, progress);
    if (progress < 1.0) {
      window.requestAnimationFrame(step);
    }
  }
  window.requestAnimationFrame(step);
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
function enableBoardDrawing(canvas, getActiveColor, getActiveSize) {
  if (!canvas || !canvas.getContext) return;
  var ctx = canvas.getContext("2d");
  var drawing = false;
  var currentStroke = null;
  window.localStrokes = []; // Phase 4: local stroke history

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
    
    currentStroke = {
      color: typeof getActiveColor === "function" ? getActiveColor() : "#F1F5F9",
      size: typeof getActiveSize === "function" ? getActiveSize() : 2.5,
      pathStr: "M" + pos.x + " " + pos.y
    };
    
    var ratio = window.devicePixelRatio || 1;
    ctx.save();
    ctx.setTransform(1, 0, 0, 1, 0, 0);
    ctx.beginPath();
    ctx.moveTo(pos.x * ratio, pos.y * ratio);
  }

  function moveDraw(e) {
    if (!drawing) return;
    e.preventDefault();
    var pos = getCanvasCoords(e);
    
    var ratio = window.devicePixelRatio || 1;
    ctx.lineTo(pos.x * ratio, pos.y * ratio);
    ctx.strokeStyle = currentStroke.color;
    ctx.lineWidth = currentStroke.size * ratio;
    ctx.lineCap = "round";
    ctx.lineJoin = "round";
    ctx.stroke();
    
    currentStroke.pathStr += " L " + pos.x + " " + pos.y;
    ctx.beginPath();
    ctx.moveTo(pos.x * ratio, pos.y * ratio);
  }

  function stopDraw(e) {
    if (!drawing) return;
    drawing = false;
    ctx.restore();
    if (currentStroke) {
      window.localStrokes.push(currentStroke);
      currentStroke = null;
    }
  }

  canvas.addEventListener("pointerdown", startDraw);
  canvas.addEventListener("pointermove", moveDraw);
  window.addEventListener("pointerup", stopDraw);
  
  // Touch specific (pointer events might not capture all touch smoothly on all older devices, but let's keep it safe)
  canvas.addEventListener("touchstart", startDraw, { passive: false });
  canvas.addEventListener("touchmove", moveDraw, { passive: false });
  window.addEventListener("touchend", stopDraw);
}

/**
 * Wires the teacher's single-tap "Start session" button.
 */
function initSessionButton(buttonEl, timerEl, onStart, onStop) {
  if (!buttonEl) return;
  var recording = false;
  var seconds = 0;
  var intervalId = null;
  var sessionId = null; // Track current session id

  buttonEl.addEventListener("click", async function () {
    recording = !recording;
    buttonEl.disabled = true; // prevent double clicks

    if (recording) {
      // Demo: Simulate starting a session locally
      sessionId = "demo-session-123";
      window.currentSessionId = sessionId;

      buttonEl.classList.add("is-recording");
      var mainLabel = buttonEl.querySelector(".label-main");
      var subLabel = buttonEl.querySelector(".label-sub");
      
      seconds = 0;
      mainLabel.textContent = "Recording…";
      subLabel.textContent = "Tap to end session";
      intervalId = window.setInterval(function () {
        seconds += 1;
        if (timerEl) timerEl.textContent = formatDuration(seconds);
      }, 1000);
      
      if (typeof showToast === "function") showToast("Live session started", "success");
      else announce("Session started");
      
      if (typeof onStart === "function") onStart(sessionId);
    } else {
      // Demo: Simulate ending a session locally
      window.clearInterval(intervalId);
      buttonEl.classList.remove("is-recording");
      var mainLabel = buttonEl.querySelector(".label-main");
      var subLabel = buttonEl.querySelector(".label-sub");
      
      mainLabel.textContent = "Start session";
      subLabel.textContent = "One tap to record and broadcast";
      
      if (typeof showToast === "function") showToast("Live session ended", "info");
      else announce("Session ended");
      
      if (typeof onStop === "function") onStop(seconds);
      window.currentSessionId = null;
    }
    buttonEl.disabled = false;
  });
}

/**
 * Wires the amber bookmark button.
 */
function initBookmarkButton(buttonEl, timerEl, listEl) {
  if (!buttonEl) return;
  buttonEl.addEventListener("click", function () {
    // For demo purposes, we always allow bookmarking
    var stamp = timerEl ? timerEl.textContent : "0:00";
    
    if (typeof showToast === "function") showToast("Moment bookmarked at " + stamp, "success");
    else announce("Moment bookmarked at " + stamp);
    
    if (listEl) {
      var item = document.createElement("li");
      item.innerHTML = 'Bookmarked at ' + stamp + ' <button class="btn btn-outline" style="padding:2px 8px; font-size:10px; border:none; margin-left:8px; color:var(--color-crimson);" onclick="this.parentElement.remove(); showToast(\'Bookmark removed\', \'info\');" aria-label="Delete bookmark">Delete</button>';
      listEl.prepend(item);
    }
    
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
