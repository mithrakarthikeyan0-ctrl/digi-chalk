/* ============================================================
   AI quiz component — student.html & quiz.html
   ============================================================ */

/**
 * INTEGRATION: replace QUIZ_DEMO with GET /api/quiz/{lessonId}.
 * Expected question shape (extends "Student.quiz.*" in the data contract):
 *   { id, prompt, options: [{id, text}], correctOptionId, explanation }
 * Questions are generated server-side from the board notes and
 * transcript of that session — the frontend renders whatever comes
 * back, in order.
 */
var QUIZ_DEMO = [
  {
    id: "q1",
    prompt: "What is 3/4 written as a decimal?",
    options: [
      { id: "a", text: "0.34" },
      { id: "b", text: "0.75" },
      { id: "c", text: "1.34" }
    ],
    correctOptionId: "b",
    explanation: "3 divided by 4 equals 0.75."
  },
  {
    id: "q2",
    prompt: "Which fraction is equivalent to 1/2?",
    options: [
      { id: "a", text: "2/4" },
      { id: "b", text: "1/3" },
      { id: "c", text: "3/5" }
    ],
    correctOptionId: "a",
    explanation: "Multiplying numerator and denominator by 2 gives 2/4."
  },
  {
    id: "q3",
    prompt: "Simplify 6/8 to its lowest terms.",
    options: [
      { id: "a", text: "3/5" },
      { id: "b", text: "2/3" },
      { id: "c", text: "3/4" }
    ],
    correctOptionId: "c",
    explanation: "Dividing both 6 and 8 by 2 simplifies to 3/4."
  }
];

function initQuiz(rootEl) {
  if (!rootEl) return;
  var current = 0;
  var score = 0;
  var selected = null;
  var studentAnswers = [];

  var promptEl = rootEl.querySelector("[data-quiz-prompt]");
  var optionsEl = rootEl.querySelector("[data-quiz-options]");
  var errorEl = rootEl.querySelector("[data-quiz-error]");
  var progressEl = rootEl.querySelector("[data-quiz-progress]");
  var progressBarEl = rootEl.querySelector("[data-quiz-progress-bar]");
  var countBadgeEl = rootEl.querySelector("[data-quiz-count-badge]");
  var nextBtn = rootEl.querySelector("[data-quiz-next]");
  var resultEl = rootEl.querySelector("[data-quiz-result]");
  var bodyEl = rootEl.querySelector("[data-quiz-body]");
  var scoreEl = rootEl.querySelector("[data-quiz-score]");
  var verdictEl = rootEl.querySelector("[data-quiz-verdict]");
  var breakdownEl = rootEl.querySelector("[data-quiz-breakdown]");

  function renderQuestion() {
    var q = QUIZ_DEMO[current];
    selected = null;
    if (errorEl) errorEl.textContent = "";
    if (promptEl) promptEl.textContent = q.prompt;

    var questionNum = current + 1;
    var totalQuestions = QUIZ_DEMO.length;
    var progressText = "Question " + questionNum + " of " + totalQuestions;
    if (progressEl) progressEl.textContent = progressText;
    if (countBadgeEl) countBadgeEl.textContent = questionNum + " of " + totalQuestions;
    if (progressBarEl) {
      var pct = Math.round((questionNum / totalQuestions) * 100);
      progressBarEl.style.width = pct + "%";
    }

    if (optionsEl) {
      optionsEl.innerHTML = "";
      var letterPrefixes = ["A", "B", "C", "D"];
      q.options.forEach(function (opt, idx) {
        var btn = document.createElement("button");
        btn.type = "button";
        btn.className = "quiz-option";
        btn.dataset.optionId = opt.id;
        btn.setAttribute("aria-pressed", "false");

        var badge = document.createElement("span");
        badge.className = "quiz-opt-letter";
        badge.textContent = letterPrefixes[idx] || (idx + 1);

        var text = document.createElement("span");
        text.className = "quiz-opt-text";
        text.textContent = opt.text;

        btn.appendChild(badge);
        btn.appendChild(text);

        btn.addEventListener("click", function () {
          selected = opt.id;
          if (errorEl) errorEl.textContent = "";
          optionsEl.querySelectorAll(".quiz-option").forEach(function (o) {
            o.setAttribute("aria-pressed", "false");
          });
          btn.setAttribute("aria-pressed", "true");
          if (typeof announce === "function") {
            announce("Selected option " + (letterPrefixes[idx] || "") + ": " + opt.text);
          }
        });

        optionsEl.appendChild(btn);
      });
    }

    if (nextBtn) {
      nextBtn.textContent = current === QUIZ_DEMO.length - 1 ? "Finish quiz" : "Next question";
    }
  }

  if (nextBtn) {
    nextBtn.addEventListener("click", function () {
      if (!selected) {
        if (errorEl) errorEl.textContent = "Pick an answer first.";
        if (typeof announce === "function") {
          announce("Please pick an answer first.");
        }
        return;
      }

      var q = QUIZ_DEMO[current];
      var isCorrect = selected === q.correctOptionId;
      if (isCorrect) score += 1;

      studentAnswers.push({
        questionId: q.id,
        prompt: q.prompt,
        selectedId: selected,
        correctId: q.correctOptionId,
        isCorrect: isCorrect,
        explanation: q.explanation
      });

      if (current < QUIZ_DEMO.length - 1) {
        current += 1;
        renderQuestion();
      } else {
        /* INTEGRATION: POST the final score & answers to the results endpoint
           so it feeds into Teacher.scores and Headmaster.classes.
           Endpoint: POST /api/quiz/{lessonId}/attempts
           Payload: { studentId: "aditi", score: score, total: QUIZ_DEMO.length, answers: studentAnswers }
        */
        if (bodyEl) bodyEl.style.display = "none";
        if (progressEl) progressEl.style.display = "none";
        if (resultEl) resultEl.style.display = "block";

        if (scoreEl) {
          scoreEl.textContent = score + " / " + QUIZ_DEMO.length;
        }

        if (verdictEl) {
          if (score === QUIZ_DEMO.length) {
            verdictEl.textContent = "Outstanding! Perfect score on today's chalk notes!";
            verdictEl.style.color = "var(--color-emerald)";
          } else if (score >= 2) {
            verdictEl.textContent = "Good work! Review the bookmarked board moments to polish.";
            verdictEl.style.color = "var(--color-indigo)";
          } else {
            verdictEl.textContent = "Keep going! Try watching the 30s recap before retesting.";
            verdictEl.style.color = "var(--color-amber)";
          }
        }

        if (breakdownEl) {
          var html = '<div class="card" style="margin-top:16px; padding:12px; border:1px solid var(--color-slate-light);">';
          html += '<h3 style="font-size:13px; margin-bottom:8px; font-weight:700;">Question Summary:</h3>';
          studentAnswers.forEach(function (ans, i) {
            var icon = ans.isCorrect
              ? '<span class="badge badge-good" style="margin-right:6px;">Correct</span>'
              : '<span class="badge badge-warn" style="margin-right:6px;">Review</span>';
            html += '<div style="padding:6px 0; border-top:1px solid var(--color-slate-light); font-size:12px;">' +
              '<div>' + icon + '<strong>Q' + (i + 1) + ':</strong> ' + ans.prompt + '</div>' +
              '<div class="caption mt-8" style="color:var(--text-secondary);">' + ans.explanation + '</div>' +
              '</div>';
          });
          html += '</div>';
          breakdownEl.innerHTML = html;
        }

        if (typeof announce === "function") {
          announce("Quiz finished. You scored " + score + " out of " + QUIZ_DEMO.length);
        }
      }
    });
  }

  var retakeBtn = rootEl.querySelector("[data-quiz-retake]");
  if (retakeBtn) {
    retakeBtn.addEventListener("click", function () {
      current = 0;
      score = 0;
      selected = null;
      studentAnswers = [];
      if (progressEl) progressEl.style.display = "";
      if (bodyEl) bodyEl.style.display = "block";
      if (resultEl) resultEl.style.display = "none";
      renderQuestion();
      if (typeof announce === "function") {
        announce("Quiz restarted. Question 1.");
      }
    });
  }

  renderQuestion();
}
