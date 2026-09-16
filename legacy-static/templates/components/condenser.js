/* ============================================================
   Lecture condenser component — student.html
   The 50-minute -> <=30s compression itself happens server-side;
   this file only plays back whatever clip URL comes from the API.
   ============================================================ */

/**
 * INTEGRATION: replace with the real recap from GET /api/lessons/{id}/recap.
 * Expected shape (data contract "Student.recaps[]"):
 *   { id: string, durationSec: number, url: string }
 * `url` is an MP4 file or HLS stream.
 * In production, the backend/CDN will provide low-bandwidth media variants
 * (e.g. lower bitrate, audio-only, or lightweight vector stroke streams).
 */
var RECAP_DEMO = { id: "recap-1", durationSec: 28, url: null };

function initCondenser(cardEl) {
  if (!cardEl) return;
  var playBtn = cardEl.querySelector("[data-condenser-play]");
  var progressFill = cardEl.querySelector("[data-condenser-progress]");
  var timeLabel = cardEl.querySelector("[data-condenser-time]");
  var playing = false;
  var elapsed = 0;
  var intervalId = null;
  var total = RECAP_DEMO.durationSec;
  var isCompleted = false;

  var playIcon = '<svg width="14" height="14" viewBox="0 0 24 28" fill="currentColor"><polygon points="8,6 20,14 8,22"></polygon></svg>';
  var pauseIcon = '<svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><rect x="6" y="5" width="4" height="14"></rect><rect x="14" y="5" width="4" height="14"></rect></svg>';
  var replayIcon = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"></path><path d="M3 3v5h5"></path></svg>';

  function formatTime(sec) {
    var m = Math.floor(sec / 60);
    var s = Math.floor(sec % 60);
    return m + ":" + (s < 10 ? "0" + s : s);
  }

  function reset() {
    elapsed = 0;
    playing = false;
    isCompleted = false;
    if (intervalId) window.clearInterval(intervalId);
    if (progressFill) progressFill.style.width = "0%";
    if (playBtn) {
      playBtn.setAttribute("aria-label", "Play recap reel");
      playBtn.innerHTML = playIcon;
    }
    if (timeLabel) {
      timeLabel.textContent = formatTime(0) + " / " + formatTime(total);
    }
  }

  function handleComplete() {
    playing = false;
    isCompleted = true;
    elapsed = total;
    if (intervalId) window.clearInterval(intervalId);
    if (playBtn) {
      playBtn.setAttribute("aria-label", "Replay recap reel");
      playBtn.innerHTML = replayIcon;
    }
    if (progressFill) progressFill.style.width = "100%";
    if (timeLabel) {
      timeLabel.innerHTML = formatTime(total) + " / " + formatTime(total) + ' &middot; <span style="color:var(--color-emerald); font-weight:700;">Completed</span>';
    }
    if (typeof announce === "function") {
      announce("Recap reel completed. Click button to replay.");
    }
  }

  if (playBtn) {
    playBtn.addEventListener("click", function () {
      if (isCompleted) {
        reset();
      }

      playing = !playing;
      playBtn.setAttribute("aria-label", playing ? "Pause recap reel" : "Play recap reel");
      playBtn.innerHTML = playing ? pauseIcon : playIcon;

      if (playing) {
        /* INTEGRATION: swap this fake progress tick for real
           <video>.play() + timeupdate listener once RECAP_DEMO.url
           is a live media source. */
        if (typeof announce === "function") {
          announce("Playing 30-second recap");
        }
        intervalId = window.setInterval(function () {
          elapsed += 1;
          if (elapsed >= total) {
            handleComplete();
            return;
          }
          if (progressFill) {
            progressFill.style.width = (elapsed / total) * 100 + "%";
          }
          if (timeLabel) {
            timeLabel.textContent = formatTime(elapsed) + " / " + formatTime(total);
          }
        }, 1000);
      } else {
        if (intervalId) window.clearInterval(intervalId);
        if (typeof announce === "function") {
          announce("Recap paused");
        }
      }
    });
  }

  reset();
  cardEl._resetReel = reset;
  cardEl._setReel = function (newTotal) {
    total = newTotal;
    RECAP_DEMO.durationSec = newTotal;
    reset();
  };
}

/**
 * Updates the reel duration dynamically when switching subjects.
 */
function updateCondenserReel(cardEl, durationSec) {
  if (!cardEl || !cardEl._setReel) return;
  cardEl._setReel(durationSec);
}
