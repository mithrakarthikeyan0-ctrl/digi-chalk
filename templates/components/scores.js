/* ============================================================
   Scores component
   Used by: teacher.html, parent.html, headmaster.html
   ============================================================ */

/**
 * Renders one score row into a container.
 * item: { label: string, value: 0-100, meta: string }
 * INTEGRATION: teacher.html sources these from
 * GET /api/scores/{classId} ("Teacher.scores.*" in the contract).
 */
function renderScoreRow(container, item) {
  var row = document.createElement("div");
  row.className = "mt-16";
  row.innerHTML =
    '<div class="row-between"><span style="font-size:12px;color:var(--text-primary)">' +
    item.label +
    '</span><span class="caption">' +
    item.meta +
    "</span></div>" +
    '<div class="bar-track mt-8"><div class="bar-fill ' +
    scoreBarClass(item.value) +
    '" style="width:' +
    item.value +
    '%"></div></div>';
  container.appendChild(row);
}

/**
 * INTEGRATION: replace with GET /api/schools/{schoolId}/classes.
 * Expected shape (data contract "Headmaster.classes[]"):
 *   { id, avgScore, interaction, flag: string | null }
 * No teacher-level fields belong in this response — see HANDOFF.md
 * Section 4 note before wiring the real query.
 */
var CLASS_DEMO = [
  { id: "Class 7A", avgScore: 54, interaction: 41, flag: "low score" },
  { id: "Class 6C", avgScore: 63, interaction: 58, flag: "low engagement" },
  { id: "Class 8B", avgScore: 81, interaction: 77, flag: null },
  { id: "Class 9A", avgScore: 88, interaction: 84, flag: null }
];

function renderClassList(container, classes) {
  container.innerHTML = "";
  classes.forEach(function (c) {
    var card = document.createElement("div");
    card.className = "card";
    var band = classifyValue(Math.min(c.avgScore, c.interaction));
    if (c.flag) card.style.borderColor = band === "low" ? "var(--color-crimson)" : "var(--color-amber)";
    var badge = c.flag
      ? '<span class="badge ' + (band === "low" ? "badge-low" : "badge-warn") + '">' + c.flag + "</span>"
      : '<span class="badge badge-good">on track</span>';
    card.innerHTML =
      '<div class="row-between"><h2>' +
      c.id +
      "</h2>" +
      badge +
      "</div>" +
      '<p class="caption mt-8">Score ' +
      c.avgScore +
      "% &middot; Engagement " +
      c.interaction +
      "%</p>" +
      '<div class="bar-track mt-8"><div class="bar-fill ' +
      band +
      '" style="width:' +
      c.avgScore +
      '%"></div></div>';
    container.appendChild(card);
  });
}

/**
 * Sorts CLASS_DEMO by the chosen key and re-renders.
 * key: "score-asc" | "score-desc" | "engagement-asc" | "engagement-desc"
 */
function initClassSort(selectEl, container) {
  if (!selectEl) return;
  function apply() {
    var key = selectEl.value;
    var sorted = CLASS_DEMO.slice().sort(function (a, b) {
      switch (key) {
        case "score-asc": return a.avgScore - b.avgScore;
        case "score-desc": return b.avgScore - a.avgScore;
        case "engagement-asc": return a.interaction - b.interaction;
        case "engagement-desc": return b.interaction - a.interaction;
        default: return 0;
      }
    });
    renderClassList(container, sorted);
  }
  selectEl.addEventListener("change", apply);
  apply();
}
