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

/**
 * Global Toast System for visual feedback.
 * Types: 'success', 'error', 'info' (default)
 */
function showToast(message, type) {
  type = type || 'info';
  var container = document.getElementById("toast-container");
  if (!container) {
    container = document.createElement("div");
    container.id = "toast-container";
    container.className = "toast-container";
    document.body.appendChild(container);
  }

  var iconSvg = "";
  if (type === 'success') {
    iconSvg = '<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><polyline points="20 6 9 17 4 12"></polyline></svg>';
  } else if (type === 'error') {
    iconSvg = '<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>';
  } else {
    iconSvg = '<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg>';
  }

  var toast = document.createElement("div");
  toast.className = "toast toast-" + type;
  toast.innerHTML = '<div class="toast-icon">' + iconSvg + '</div><span>' + message + '</span>';
  
  container.appendChild(toast);
  announce(message); // Ensure screen readers also get it
  
  // Trigger reflow to animate in
  void toast.offsetWidth;
  toast.classList.add("toast-show");
  
  setTimeout(function() {
    toast.classList.remove("toast-show");
    setTimeout(function() {
      if (toast.parentNode) toast.parentNode.removeChild(toast);
    }, 300);
  }, 3000);
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

/**
 * LocalStorage wrapper for safe parsing and saving.
 */
var LocalDB = {
  get: function(key, def) {
    try {
      var val = localStorage.getItem("digichalk_" + key);
      return val ? JSON.parse(val) : def;
    } catch(e) {
      return def;
    }
  },
  set: function(key, val) {
    try {
      localStorage.setItem("digichalk_" + key, JSON.stringify(val));
    } catch(e) {
      console.warn("LocalStorage failed", e);
    }
  },
  remove: function(key) {
    try {
      localStorage.removeItem("digichalk_" + key);
    } catch(e) {}
  },
  resetAll: function() {
    var keys = Object.keys(localStorage);
    keys.forEach(function(k) {
      if (k.startsWith("digichalk_")) {
        localStorage.removeItem(k);
      }
    });
  }
};

/**
 * Global Topbar Logic: Wires the Search, Notifications, and Profile buttons.
 */
function wireGlobalTopbar() {
  var searchBtn = document.querySelector("[data-global-search]");
  var notifyBtn = document.querySelector("[data-global-notify]");
  var profileBtn = document.querySelector("[data-global-profile]");

  if (searchBtn) {
    searchBtn.addEventListener("click", function() {
      var html = '<input type="text" placeholder="Search lessons, students, or classes..." class="form-input" style="width:100%; margin-bottom:12px;" autofocus>' +
                 '<div class="card" style="padding:12px; text-align:center;"><p class="caption">Type to search...</p></div>';
      openModal("Search", html);
    });
  }

  if (notifyBtn) {
    notifyBtn.addEventListener("click", function() {
      var notifs = LocalDB.get("notifications", [
        { id: 1, text: "New assignment: Fractions worksheet", read: false },
        { id: 2, text: "Class 8B Maths starts in 10 mins", read: false }
      ]);
      
      var html = '<div id="notifList">';
      if (notifs.length === 0) {
        html += '<p class="caption" style="text-align:center;">No new notifications</p>';
      } else {
        notifs.forEach(function(n) {
          html += '<div class="card mt-8" style="padding:12px; display:flex; justify-content:space-between; align-items:center;">' +
                  '<div style="' + (n.read ? 'opacity:0.6;' : 'font-weight:600;') + '">' + n.text + '</div>' +
                  '<button class="btn btn-outline" style="padding:4px 8px; font-size:11px;" onclick="markNotifRead(' + n.id + ')">Dismiss</button>' +
                  '</div>';
        });
      }
      html += '</div><button class="btn btn-outline btn-block mt-16" onclick="clearNotifs()">Clear all</button>';
      
      openModal("Notifications", html);
    });
  }

  if (profileBtn) {
    profileBtn.addEventListener("click", function() {
      var lang = LocalDB.get("lang", "en");
      var html = '<div class="card" style="padding:12px;">' +
                 '<p class="caption mb-8">Preferences</p>' +
                 '<div class="row-between"><span>Language</span><select class="form-input" style="width:auto; padding:4px 8px;" id="globalLangSelect"><option value="en" ' + (lang==="en"?"selected":"") + '>English</option><option value="ta" ' + (lang==="ta"?"selected":"") + '>தமிழ்</option></select></div>' +
                 '<div class="row-between mt-16"><span>Text Size</span><button class="btn btn-outline" style="padding:4px 8px;" id="globalTextSizeBtn">Toggle Large Text</button></div>' +
                 '</div>' +
                 '<div class="card mt-16" style="padding:12px; border-color:var(--color-crimson);">' +
                 '<p class="caption mb-8" style="color:var(--color-crimson);">Danger Zone</p>' +
                 '<button class="btn btn-outline btn-block" style="color:var(--color-crimson); border-color:var(--color-crimson);" id="globalResetBtn">Reset Demo Data</button>' +
                 '</div>';
      openModal("Settings & Profile", html);
      
      document.getElementById("globalLangSelect").addEventListener("change", function(e) {
        LocalDB.set("lang", e.target.value);
        showToast("Language updated to " + e.target.value, "success");
      });
      document.getElementById("globalTextSizeBtn").addEventListener("click", function() {
        var current = document.body.classList.contains("text-large");
        if (current) document.body.classList.remove("text-large");
        else document.body.classList.add("text-large");
        LocalDB.set("textSize", !current);
        showToast("Text size updated", "success");
      });
      document.getElementById("globalResetBtn").addEventListener("click", function() {
        if (confirm("Are you sure you want to delete all local demo data?")) {
          LocalDB.resetAll();
          showToast("Data reset successfully", "success");
          setTimeout(function() { window.location.reload(); }, 1000);
        }
      });
    });
  }
  
  // Apply saved text size on load
  if (LocalDB.get("textSize", false)) {
    document.body.classList.add("text-large");
  }
}

// Notification helpers (global so inline onclicks can reach them)
window.markNotifRead = function(id) {
  var notifs = LocalDB.get("notifications", [
    { id: 1, text: "New assignment: Fractions worksheet", read: false },
    { id: 2, text: "Class 8B Maths starts in 10 mins", read: false }
  ]);
  notifs = notifs.map(function(n) { if (n.id === id) n.read = true; return n; });
  LocalDB.set("notifications", notifs);
  showToast("Notification dismissed", "info");
  document.querySelector("[data-global-notify]").click(); // Refresh modal
};
window.clearNotifs = function() {
  LocalDB.set("notifications", []);
  showToast("All notifications cleared", "info");
  document.querySelector("[data-global-notify]").click();
};

document.addEventListener("DOMContentLoaded", wireGlobalTopbar);

