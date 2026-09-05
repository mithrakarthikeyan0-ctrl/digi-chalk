const { chromium } = require('playwright');

const pages = [
  'index/index.html',
  'index/teacher.html',
  'index/student.html',
  'index/parent.html',
  'index/headmaster.html',
  'index/quiz.html',
  'index/replay.html',
  'index/board.html?role=teacher',
  'index/board.html?role=student',
];

(async () => {
  const launchOptions = process.env.PLAYWRIGHT_CHROME_PATH
    ? { executablePath: process.env.PLAYWRIGHT_CHROME_PATH }
    : (process.platform === 'win32' ? { channel: 'msedge' } : {});
  const browser = await chromium.launch(launchOptions);
  let hadError = false;

  for (const p of pages) {
    const page = await browser.newPage({ viewport: { width: 380, height: 760 } });
    const pageErrors = [];
    page.on('pageerror', (err) => pageErrors.push('pageerror: ' + err.message));
    page.on('response', (res) => {
      const url = res.url();
      if (res.status() >= 400 && !url.includes('fonts.g') && !url.includes('favicon')) {
        pageErrors.push('http ' + res.status() + ': ' + url);
      }
    });
    page.on('requestfailed', (req) => {
      // Ignore Google Fonts — no network egress in this sandbox, expected to fail here.
      if (!req.url().includes('fonts.g')) {
        pageErrors.push('requestfailed: ' + req.url() + ' -> ' + (req.failure() && req.failure().errorText));
      }
    });

    await page.goto('http://localhost:8123/' + p, { waitUntil: 'load', timeout: 15000 });
    await page.waitForTimeout(1500); // let skeleton -> real-content swap resolve

    console.log('---', p, '---');
    if (pageErrors.length) {
      hadError = true;
      pageErrors.forEach((e) => console.log('  ' + e));
    } else {
      console.log('  no console/page errors');
    }

    await page.close();
  }

  await browser.close();
  process.exit(hadError ? 1 : 0);
})();
