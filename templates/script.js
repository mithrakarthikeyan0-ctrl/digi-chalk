/* ============================================================
   Digi-Chalk / Samarthya — shared logic
   Loaded on every page. Feature-specific logic lives in
   templates/components/*.js
   ============================================================ */

/**
 * Simulates a network fetch delay so every screen can show its
 * skeleton state the way it will on a slow connection.
 *
 * INTEGRATION: replace this whole function with real fetch() calls.
 * Each page's loader currently calls `simulateLoad(el, callback)`
 * where `callback` fills in the real DOM content — swap the
 * setTimeout for an actual request and call `callback(data)` with
 * the response once it resolves. Keep the data-loaded="true" toggle,
 * the CSS keys off it to hide skeletons / reveal real content.
 */
function simulateLoad(root, onReady, delayMs) {
  if (!root) return;
  var delay = typeof delayMs === "number" ? delayMs : 700 + Math.random() * 500;
  root.setAttribute("data-loaded", "false");
  window.setTimeout(function () {
    if (typeof onReady === "function") onReady();
    root.setAttribute("data-loaded", "true");
  }, delay);
}

/** Wires a .switch checkbox to fire a callback with the new boolean state. */
function bindSwitch(inputEl, onChange) {
  if (!inputEl) return;
  inputEl.addEventListener("change", function () {
    onChange(inputEl.checked);
  });
}

/** Wires a .chip-row so exactly one chip is aria-pressed at a time. */
function bindChipRow(rowEl, onSelect) {
  if (!rowEl) return;
  var chips = rowEl.querySelectorAll(".chip");
  chips.forEach(function (chip) {
    chip.addEventListener("click", function () {
      chips.forEach(function (c) { c.setAttribute("aria-pressed", "false"); });
      chip.setAttribute("aria-pressed", "true");
      onSelect(chip.dataset.value, chip);
    });
  });
}

/**
 * Single source of truth for score/engagement color bands, used by
 * score bars, badges, and card borders alike so a value is never
 * shown as one color in the bar and another in its badge.
 *   good  >= 75
 *   warn  60–74
 *   low   < 60
 */
function classifyValue(value) {
  if (value >= 75) return "good";
  if (value >= 60) return "warn";
  return "low";
}

/** Picks the score-bar color class from a 0–100 value. */
function scoreBarClass(value) {
  return classifyValue(value);
}

/** mm:ss formatter for session timers / recap durations. */
function formatDuration(totalSeconds) {
  var m = Math.floor(totalSeconds / 60);
  var s = Math.floor(totalSeconds % 60);
  return m + ":" + (s < 10 ? "0" : "") + s;
}

/**
 * Live region announcer for status changes (recording started,
 * quiz submitted, etc.) so low-tech-literacy / screen-reader users
 * get a spoken confirmation instead of relying on a visual toast alone.
 */
function announce(message) {
  var region = document.getElementById("live-region");
  if (!region) {
    region = document.createElement("div");
    region.id = "live-region";
    region.className = "visually-hidden";
    region.setAttribute("aria-live", "polite");
    document.body.appendChild(region);
  }
  region.textContent = "";
  window.setTimeout(function () { region.textContent = message; }, 50);
}

/** Highlights the current page's bottom-nav item based on data-nav-current on <body>. */
document.addEventListener("DOMContentLoaded", function () {
  var current = document.body.getAttribute("data-nav-current");
  if (!current) return;
  var link = document.querySelector('.bottomnav [data-nav="' + current + '"]');
  if (link) link.classList.add("active");
});

/**
 * Reusable modal/bottom-sheet manager for secondary navigation,
 * "View all" score rosters, and profile information without dead links.
 */
function openModal(title, contentHtml) {
  var backdrop = document.getElementById("appModal");
  if (!backdrop) {
    backdrop = document.createElement("div");
    backdrop.id = "appModal";
    backdrop.className = "modal-backdrop";
    backdrop.setAttribute("role", "dialog");
    backdrop.setAttribute("aria-modal", "true");
    backdrop.innerHTML =
      '<div class="modal-sheet">' +
        '<div class="modal-header">' +
          '<h2 style="font-size:17px; margin:0;" id="appModalTitle"></h2>' +
          '<button class="modal-close-btn" id="appModalClose" aria-label="Close dialog">&times;</button>' +
        '</div>' +
        '<div id="appModalContent"></div>' +
      '</div>';
    document.body.appendChild(backdrop);

    backdrop.addEventListener("click", function (e) {
      if (e.target === backdrop) closeModal();
    });
    document.getElementById("appModalClose").addEventListener("click", closeModal);
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape") closeModal();
    });
  }

  document.getElementById("appModalTitle").textContent = title;
  document.getElementById("appModalContent").innerHTML = contentHtml;
  backdrop.classList.add("is-open");
  announce(title + " opened");
}

function closeModal() {
  var backdrop = document.getElementById("appModal");
  if (backdrop) {
    backdrop.classList.remove("is-open");
    announce("Dialog closed");
  }
}

/**
 * Secondary bottom nav handler: prevents unhandled '#' navigation
 * and renders a contextual sheet for secondary views.
 */
function wireSecondaryNav() {
  document.querySelectorAll('.bottomnav a[href="#"], .bottomnav button').forEach(function (btn) {
    btn.addEventListener("click", function (e) {
      e.preventDefault();
      var navKey = btn.getAttribute("data-nav") || "details";
      var label = btn.textContent.trim();
      var role = document.title.split("—")[1] ? document.title.split("—")[1].trim() : "Digi-Chalk";
      
      var content = "";
      if (navKey === "profile") {
        content = '<div class="card" style="box-shadow:none; border:1px solid var(--color-slate-light);">' +
          '<div style="display:flex; align-items:center; gap:12px;">' +
            '<div class="avatar" style="width:48px; height:48px; font-size:18px;">DC</div>' +
            '<div>' +
              '<div style="font-weight:700; font-size:15px;">' + role + ' Account</div>' +
              '<div class="caption">Sunrise Public School &middot; District 4</div>' +
            '</div>' +
          '</div>' +
          '<div class="mt-16" style="border-top:1px dashed var(--color-slate-light); padding-top:12px;">' +
            '<div class="row-between"><span class="caption">Language</span><span style="font-size:12px; font-weight:600;">English / தமிழ்</span></div>' +
            '<div class="row-between mt-8"><span class="caption">Network Data Saving</span><span class="badge badge-good">Optimized</span></div>' +
            '<div class="row-between mt-8"><span class="caption">Sync Status</span><span class="badge badge-good">Up to date</span></div>' +
          '</div>' +
        '</div>' +
        '<div class="mt-16"><a href="index.html" class="btn btn-outline btn-block">&larr; Switch role / Sign out</a></div>';
      } else if (navKey === "sessions") {
        content = '<p class="caption">Recent classroom recordings and live board broadcasts:</p>' +
          '<div class="mt-8">' +
            '<div class="card mt-8" style="padding:12px;">' +
              '<div class="row-between"><span style="font-weight:700; font-size:13px;">Class 8B &middot; Maths</span><span class="badge badge-good">Today 10:15 AM</span></div>' +
              '<p class="caption mt-8">Fractions &amp; Decimals &middot; 48 min &middot; 2 bookmarks</p>' +
            '</div>' +
            '<div class="card mt-8" style="padding:12px;">' +
              '<div class="row-between"><span style="font-weight:700; font-size:13px;">Class 7A &middot; Geometry</span><span class="badge" style="background:#E2E4DD;">Yesterday</span></div>' +
              '<p class="caption mt-8">Angles &amp; Triangles &middot; 42 min &middot; 1 bookmark</p>' +
            '</div>' +
          '</div>';
      } else if (navKey === "scores" || navKey === "classes" || navKey === "reports") {
        content = '<p class="caption">Performance and assessment records:</p>' +
          '<div class="card mt-8" style="padding:12px;">' +
            '<div class="row-between"><span style="font-weight:600; font-size:13px;">Class average test score</span><span style="font-weight:700; color:var(--color-emerald);">78%</span></div>' +
            '<div class="row-between mt-8"><span class="caption">Quizzes completed</span><span style="font-weight:600; font-size:12px;">148 / 160</span></div>' +
            '<div class="row-between mt-8"><span class="caption">Low-bandwidth offline submissions</span><span style="font-weight:600; font-size:12px;">32 syncs</span></div>' +
          '</div>';
      } else if (navKey === "messages") {
        content = '<p class="caption">Automated SMS &amp; WhatsApp digests sent to parents:</p>' +
          '<div class="card mt-8" style="padding:12px;">' +
            '<div class="row-between"><span class="caption" style="color:var(--color-emerald-dark); font-weight:700;">WhatsApp &middot; 2:14 pm</span><span class="badge badge-good">Delivered</span></div>' +
            '<p style="font-size:12px; margin-top:6px;">Aditi completed "Fractions" quiz — scored 4/5.</p>' +
          '</div>' +
          '<div class="card mt-8" style="padding:12px;">' +
            '<div class="row-between"><span class="caption" style="color:var(--color-slate); font-weight:700;">SMS &middot; Yesterday</span><span class="badge badge-good">Delivered</span></div>' +
            '<p style="font-size:12px; margin-top:6px;">Homework assigned: Fractions practice page 42.</p>' +
          '</div>';
      } else if (navKey === "reels") {
        content = '<p class="caption">Condensed 30-second video/stroke reels for quick revision:</p>' +
          '<div class="card mt-8" style="padding:12px;">' +
            '<div class="row-between"><span style="font-weight:700; font-size:13px;">Maths: Fractions chapter 4</span><span class="badge badge-good">28s</span></div>' +
            '<p class="caption mt-8">50 min class condensed into key chalkboard moments.</p>' +
          '</div>';
      } else {
        content = '<p class="caption">No additional items for ' + label + '.</p>';
      }

      openModal(label, content);
    });
  });
}

document.addEventListener("DOMContentLoaded", wireSecondaryNav);

/**
 * Multi-child demo data for parent.html
 * INTEGRATION: Replace PARENT_CHILDREN_DEMO with GET /api/parents/{id}
 */
var PARENT_CHILDREN_DEMO = {
  aditi: {
    name: "Aditi",
    grade: "8B",
    subject: "Maths",
    unitTestScore: 82,
    scoreDelta: "Up 6 pts from last test",
    summaryEn: "Today Aditi covered fractions: writing them as decimals and simplifying to lowest terms. She completed the in-class quiz and marked two teacher bookmarks for revision.",
    summaryTa: "இன்று அதிதி பின்னங்கள் தலைப்பை கற்றார்: தசமங்களாக மாற்றுதல் மற்றும் எளிய வடிவில் எழுதுதல். வகுப்பறை வினாடி வினாவை முடித்து, ஆசிரியர் குறித்த இரண்டு முக்கிய பகுதிகளை தேர்வுக்காக குறித்து வைத்தார்.",
    scores: [
      { label: "Fractions quiz", value: 80, meta: "" },
      { label: "Science unit test", value: 56, meta: "" },
      { label: "English grammar", value: 88, meta: "" }
    ],
    recentAlert: "Aditi completed “Fractions” quiz — scored 4/5.",
    alertTime: "2:14 pm"
  },
  rohan: {
    name: "Rohan",
    grade: "5A",
    subject: "Science",
    unitTestScore: 74,
    scoreDelta: "Up 10 pts from last test",
    summaryEn: "Today Rohan learned about plant parts and photosynthesis in Science. He drew the leaf structure diagram and participated in the chalk quiz.",
    summaryTa: "இன்று ரோகன் அறிவியலில் தாவர பாகங்கள் மற்றும் ஒளிச்சேர்க்கை பற்றி கற்றார். இலை அமைப்பு வரைபடத்தை வரைந்து, வினாடி வினாவில் பங்கேற்றார்.",
    scores: [
      { label: "Plant biology quiz", value: 75, meta: "" },
      { label: "Maths multiplication", value: 70, meta: "" },
      { label: "Social studies map", value: 65, meta: "" }
    ],
    recentAlert: "Rohan completed “Plant biology” quiz — scored 3/5.",
    alertTime: "11:30 am"
  }
};

