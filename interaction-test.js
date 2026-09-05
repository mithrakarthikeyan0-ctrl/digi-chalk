const { chromium } = require('playwright');
const assert = require('assert');

const BASE = 'http://localhost:8123/index/';

(async () => {
  const launchOptions = process.env.PLAYWRIGHT_CHROME_PATH
    ? { executablePath: process.env.PLAYWRIGHT_CHROME_PATH }
    : (process.platform === 'win32' ? { channel: 'msedge' } : {});
  const browser = await chromium.launch(launchOptions);
  const page = await browser.newPage({ viewport: { width: 380, height: 760 } });
  const errors = [];
  page.on('pageerror', (e) => errors.push('pageerror: ' + e.message));

  // ---------- Teacher: start session + bookmark ----------
  await page.goto(BASE + 'teacher.html', { waitUntil: 'load' });
  await page.waitForSelector('[data-loaded="true"]', { timeout: 5000 });
  await page.click('#sessionBtn');
  await page.waitForTimeout(1200);
  const timerText = await page.textContent('#sessionTimer');
  assert(timerText !== '0:00', 'Teacher: session timer should advance after starting, got ' + timerText);
  const recording = await page.evaluate(() => document.getElementById('sessionBtn').classList.contains('is-recording'));
  assert(recording, 'Teacher: Start session button should flip to recording state');
  await page.click('#bookmarkBtn');
  const bookmarkCount = await page.evaluate(() => document.getElementById('bookmarkList').children.length);
  assert(bookmarkCount === 1, 'Teacher: bookmark should add one list entry, got ' + bookmarkCount);
  console.log('PASS teacher: start session + bookmark');

  // score bars actually rendered
  const scoreBars = await page.evaluate(() => document.querySelectorAll('#scoreRows .bar-fill').length);
  assert(scoreBars === 3, 'Teacher: expected 3 score rows, got ' + scoreBars);
  console.log('PASS teacher: score rows rendered');

  // ---------- Student: chips, low-bandwidth toggle, condenser ----------
  await page.goto(BASE + 'student.html', { waitUntil: 'load' });
  await page.waitForSelector('[data-loaded="true"]', { timeout: 5000 });
  await page.click('.chip[data-value="science"]');
  const scienceState = await page.getAttribute('.chip[data-value="science"]', 'aria-pressed');
  const mathsState = await page.getAttribute('.chip[data-value="maths"]', 'aria-pressed');
  assert(scienceState === 'true' && mathsState === 'false', 'Student: chip selection should be exclusive');
  console.log('PASS student: subject chips exclusive select');

  const beforeToggle = await page.isChecked('#lowBandwidthToggle');
  await page.click('label:has(#lowBandwidthToggle) .track'); // real users tap the visible track; input is visually hidden by design
  const afterToggle = await page.isChecked('#lowBandwidthToggle');
  assert(beforeToggle !== afterToggle, 'Student: low-bandwidth switch should flip state');
  console.log('PASS student: low-bandwidth toggle');

  await page.click('#condenserPlay');
  await page.waitForTimeout(1600);
  const progressWidth = await page.evaluate(() => document.querySelector('[data-condenser-progress]').style.width);
  assert(progressWidth !== '0%', 'Student: recap progress should advance after play, got ' + progressWidth);
  console.log('PASS student: condenser playback progresses');

  // ---------- Quiz: validation + scoring flow ----------
  await page.goto(BASE + 'quiz.html', { waitUntil: 'load' });
  await page.click('[data-quiz-next]'); // no option picked yet
  const err = await page.textContent('[data-quiz-error]');
  assert(err.includes('Pick an answer'), 'Quiz: should block advancing with no answer selected');
  console.log('PASS quiz: blocks empty submission');

  for (let i = 0; i < 3; i++) {
    await page.click('.quiz-option:first-child');
    await page.click('[data-quiz-next]');
  }
  const resultVisible = await page.evaluate(() => document.querySelector('[data-quiz-result]').style.display === 'block');
  assert(resultVisible, 'Quiz: result screen should show after final question');
  const scoreText = await page.textContent('[data-quiz-score]');
  assert(/\d \/ 3/.test(scoreText), 'Quiz: score should render as "n / 3", got ' + scoreText);
  console.log('PASS quiz: completes and scores ->', scoreText.trim());

  // ---------- Parent: child switcher ----------
  await page.goto(BASE + 'parent.html', { waitUntil: 'load' });
  await page.waitForSelector('[data-loaded="true"]', { timeout: 5000 });
  await page.click('.child-pill[data-value="rohan"]');
  const rohanState = await page.getAttribute('.child-pill[data-value="rohan"]', 'aria-pressed');
  const aditiState = await page.getAttribute('.child-pill[data-value="aditi"]', 'aria-pressed');
  assert(rohanState === 'true' && aditiState === 'false', 'Parent: child switcher should be exclusive');
  console.log('PASS parent: child switcher exclusive select');

  // ---------- Admin: sort reorders + flags ----------
  await page.goto(BASE + 'headmaster.html', { waitUntil: 'load' });
  await page.waitForSelector('[data-loaded="true"]', { timeout: 5000 });
  const firstClassAsc = await page.textContent('#classList .card:first-child h2');
  assert(firstClassAsc.trim() === 'Class 7A', 'Admin: default sort should surface the lowest score first, got ' + firstClassAsc);
  await page.selectOption('#sortSelect', 'score-desc');
  const firstClassDesc = await page.textContent('#classList .card:first-child h2');
  assert(firstClassDesc.trim() === 'Class 9A', 'Admin: score-desc sort should surface the highest score first, got ' + firstClassDesc);
  console.log('PASS admin: sort control reorders class list');
  const bodyText = await page.textContent('body');
  assert(!/Mr\.|Mrs\.|Teacher:/i.test(bodyText), 'Admin: no teacher-identifying text should appear on this page');
  console.log('PASS admin: no teacher-level identifiers present');

  // ---------- Board: portrait rotate-guard ----------
  // default `page` viewport is 380x760 (portrait) — board.html should hide
  // the board and show the "rotate your device" prompt.
  await page.goto(BASE + 'board.html?role=teacher', { waitUntil: 'load' });
  const guardVisibleInPortrait = await page.isVisible('.rotate-guard');
  const boardHiddenInPortrait = !(await page.isVisible('.board-full'));
  assert(guardVisibleInPortrait && boardHiddenInPortrait, 'Board: portrait orientation should show the rotate prompt and hide the board');
  console.log('PASS board: portrait rotate-guard blocks the board as intended');

  // ---------- Board: role-based controls (landscape, its real orientation) ----------
  const landscapePage = await browser.newPage({ viewport: { width: 760, height: 380 } });
  await landscapePage.goto(BASE + 'board.html?role=teacher', { waitUntil: 'load' });
  const teacherCtrlVisible = await landscapePage.isVisible('#teacherControls');
  const studentCtrlHidden = !(await landscapePage.isVisible('#studentControls'));
  assert(teacherCtrlVisible && studentCtrlHidden, 'Board: teacher role should see bookmark control, not mute control');
  console.log('PASS board: teacher role shows correct controls (landscape)');

  await landscapePage.goto(BASE + 'board.html?role=student', { waitUntil: 'load' });
  const studentCtrlVisible = await landscapePage.isVisible('#studentControls');
  const teacherCtrlHidden = !(await landscapePage.isVisible('#teacherControls'));
  assert(studentCtrlVisible && teacherCtrlHidden, 'Board: student role should see mute control, not bookmark control');
  console.log('PASS board: student role shows correct controls (landscape)');
  await landscapePage.close();

  // ---------- Replay: scrubber + bookmark jump ----------
  await page.goto(BASE + 'replay.html', { waitUntil: 'load' });
  await page.click('.bookmark-dot[data-jump="0.66"]');
  const clock = await page.textContent('#replayClock');
  assert(!clock.startsWith('0:00'), 'Replay: clicking a bookmark should jump the clock forward, got ' + clock);
  console.log('PASS replay: bookmark jump moves playhead ->', clock.trim());

  if (errors.length) {
    console.log('UNCAUGHT PAGE ERRORS:', errors);
    process.exitCode = 1;
  } else {
    console.log('\nALL INTERACTION TESTS PASSED, NO PAGE ERRORS');
  }

  await browser.close();
})().catch((e) => {
  console.error('TEST FAILURE:', e.message);
  process.exit(1);
});
