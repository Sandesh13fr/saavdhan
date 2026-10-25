import assert from 'node:assert/strict';
import { mkdir, readFile, readdir, stat, unlink, writeFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import { chromium } from 'playwright';

const baseURL = process.env.BASE_URL || 'http://localhost:8123';
const origin = new URL(baseURL);
assert(['localhost', '127.0.0.1', '[::1]'].includes(origin.hostname), 'Capture requires a local backend.');
const output = new URL('../../docs/screenshots/', import.meta.url);
const timeout = 20_000;
const maxBytes = 1_500_000;
const results = [];
const warnings = [];
const descriptions = {
  '01-home': 'Home: "Before you pay. Before you fly." with the three-step strip (mock 01).',
  '02-submit': 'Submit: stepper, Paste chat / Upload file tabs and Review details CTA (mock 02).',
  '03-review': 'Review: facts read from the Bangkok demo offer, with missing values marked (mock 03).',
  '04-result-stop': 'Bangkok demo STOP result: stop sign, verdict strip, recruiter-list line and every rule row (mock 04).',
  '05-evidence': 'Evidence: offer chat with the quoted line linked to the flagged rule (mock 07).',
  '06-result-verify': 'Dubai near-miss demo: VERIFY FIRST result with points to check and passed checks (mock 05).',
  '07-safety-setup': 'Check-in plan form with synthetic aliases and the 24-hour ring (mock 08).',
  '08-checkin': 'Traveller check-in clock, I\'m okay action, timeline and demo skip control (mock 09).',
  '09-missed': 'Check-in missed after the demo clock moved forward three times.',
  '10-family': 'Simulated family alert with report ZIP link (mock 10).',
  '11-help': 'Get help directory, report ZIP and limits (mock 11).',
  '12-login': 'Institutional access login (mock 12).',
  '13-map': 'Synthetic pattern map with stats and highlighted districts, no basemap (mock 13).',
  '14-pattern': 'Repeated agent hash linked to its districts (mock 14).',
  '15-hindi': 'Bangkok demo STOP result in Hindi.',
  '16-marathi': 'Bangkok demo STOP result in Marathi.',
};
const STEPS = Object.keys(descriptions).length;

await mkdir(output, { recursive: true });
for (const name of await readdir(output)) if (name.endsWith('.png')) await unlink(new URL(name, output));
const browser = await chromium.launch();
try {
  for (const viewport of [
    { name: 'mobile', width: 390, height: 844, deviceScaleFactor: 2 },
    { name: 'desktop', width: 1366, height: 900, deviceScaleFactor: 1 },
  ]) {
    const context = await browser.newContext({
      baseURL, viewport: { width: viewport.width, height: viewport.height },
      deviceScaleFactor: viewport.deviceScaleFactor, locale: 'en-IN', timezoneId: 'Asia/Kolkata',
      reducedMotion: 'reduce',
    });
    context.setDefaultTimeout(timeout);
    context.setDefaultNavigationTimeout(timeout);
    const page = await context.newPage();
    const warn = message => {
      if (warnings.includes(`${viewport.name}: ${message}`)) return;
      warnings.push(`${viewport.name}: ${message}`);
      console.warn(`WARN ${viewport.name}: ${message}`);
    };
    const setLang = code => page.locator('header select').selectOption(code);
    const h1 = text => page.getByRole('heading', { level: 1, name: text }).waitFor();
    const capture = async (name) => {
      await page.evaluate(() => document.fonts.ready);
      assert(!/\bsafe\b/i.test(await page.locator('body').innerText()), 'Unexpected verdict wording.');
      const overflow = await page.evaluate(() => document.documentElement.scrollWidth - innerWidth);
      if (overflow > 0) warn(`${name}: horizontal overflow ${overflow}px`);
      await page.evaluate(() => window.scrollTo(0, 0));
      const filename = `${name}-${viewport.name}.png`;
      const path = fileURLToPath(new URL(filename, output));
      const options = { path, type: 'png', animations: 'disabled', fullPage: true };
      await page.screenshot(options);
      let scale = 'device';
      if ((await stat(path)).size >= maxBytes) { await page.screenshot({ ...options, scale: 'css' }); scale = 'css'; }
      const bytes = await readFile(path);
      assert(bytes.subarray(0, 8).equals(Buffer.from([137, 80, 78, 71, 13, 10, 26, 10])), 'Invalid PNG.');
      assert(bytes.length > 100 && bytes.length < maxBytes, `PNG size out of bounds: ${bytes.length}`);
      const result = { filename, bytes: bytes.length, width: bytes.readUInt32BE(16), height: bytes.readUInt32BE(20), scale };
      results.push(result);
      console.log(`OK ${filename}: ${result.bytes} bytes (${result.width}x${result.height}, ${scale} scale)`);
    };
    const step = async (name, action) => {
      try { await action(); await capture(name); } catch (error) {
        results.push({ filename: `${name}-${viewport.name}.png`, error: error.message });
        console.error(`FAIL ${name}-${viewport.name}: ${error.message}`);
      }
    };
    const demo = async (match) => {
      await page.getByRole('button', { name: 'Demo', exact: true }).click();
      await page.getByRole('button', { name: match }).click();
      await h1('Does this look right?');
    };
    let bangkok = '';
    let checkinRoute = '';
    try {
      await step('01-home', async () => { await page.goto('/'); await setLang('en'); await h1('Before you pay. Before you fly.'); });
      await step('02-submit', async () => { await page.getByRole('link', { name: 'Check my offer' }).click(); await h1("Let's check your offer."); });
      await step('03-review', async () => { await demo(/Bangkok/); bangkok = page.url().replace('/review/', '/result/'); });
      await step('04-result-stop', async () => {
        await page.getByRole('link', { name: 'See result' }).click();
        await h1(/STOP/);
        const ra = await page.locator('.ra-line').first().innerText();
        if (!/\d{4}-\d{2}-\d{2}/.test(ra)) warn(`Recruiter-list date unavailable in the app: ${ra}`);
        await page.getByRole('button', { name: /Tourist visa is not for jobs/ }).click();
      });
      await step('05-evidence', async () => {
        await page.getByRole('link', { name: 'See the evidence' }).click();
        await h1('See why it was flagged.');
        await page.locator('.bubble.is-hit').first().waitFor();
        const zip = await page.request.get(await page.getByRole('link', { name: 'Download report' }).getAttribute('href'));
        assert(zip.ok() && (await zip.body()).subarray(0, 2).toString() === 'PK', 'Report packet is not a ZIP.');
      });
      await step('06-result-verify', async () => {
        await demo(/Dubai/);
        await page.getByRole('link', { name: 'See result' }).click();
        await h1(/VERIFY/);
      });
      await step('07-safety-setup', async () => {
        await page.goto(bangkok);
        await h1(/STOP/);
        await page.getByRole('link', { name: 'Make a check-in plan' }).click();
        await h1('Keep family close.');
        await page.getByPlaceholder('Your alias (not your real name)').fill('Student (demo)');
        await page.getByPlaceholder('Name or alias').first().fill('Brother (demo)');
        await page.getByPlaceholder('How to reach them').first().fill('SMS (simulated)');
        await page.getByPlaceholder('Name or alias').nth(1).fill('Mother (demo)');
        await page.getByPlaceholder('How to reach them').nth(1).fill('Call (simulated)');
        await page.getByRole('button', { name: 'Add trip details' }).click();
        await page.getByLabel('Travel plan').fill('Pune -> Bangkok (demo)');
        await page.getByLabel('I have their permission.').check();
      });
      await step('08-checkin', async () => {
        await page.getByRole('button', { name: 'Create check-in plan' }).click();
        await h1('Time to check in.');
        checkinRoute = page.url();
      });
      await step('09-missed', async () => {
        const clock = page.getByRole('button', { name: /move the clock/ });
        for (let i = 0; i < 3; i++) {
          const response = page.waitForResponse(r => r.url().endsWith('/api/demo/advance-clock') && r.request().method() === 'POST');
          await clock.click();
          assert((await response).ok(), 'Demo clock request failed.');
          await page.waitForFunction(() => !document.querySelector('[aria-busy="true"]'));
        }
        await h1('Check-in missed.');
      });
      await step('10-family', async () => {
        await page.getByRole('link', { name: 'See the family view' }).click();
        await h1('Check-in missed.');
        await page.getByText(/Simulated alert: Student \(demo\) missed a check-in/).first().waitFor();
      });
      await step('11-help', async () => { await page.getByRole('link', { name: 'Reporting options' }).click(); await h1('Find the right help.'); });
      await step('12-login', async () => { await page.goto('/#/login'); await h1('Institutional access'); });
      await step('13-map', async () => {
        await page.getByPlaceholder('Email').fill('officer@saavdhan.example');
        await page.getByPlaceholder('Password').fill('screenshot-officer-pw-2026');
        await page.getByRole('button', { name: 'Enter demo' }).click();
        await h1('Patterns, at a glance.');
        await page.waitForFunction(() => document.querySelectorAll('path.leaflet-interactive').length > 0);
        assert(await page.locator('path.leaflet-interactive[stroke="#c62828"]').count() > 0, 'No districts highlighted.');
        assert.equal(await page.locator('.leaflet-tile').count(), 0, 'Unexpected basemap tiles.');
      });
      await step('14-pattern', async () => {
        await page.getByRole('link', { name: 'Explore patterns' }).click();
        await h1(/^One (contact|template)\./);
        await page.getByText('Hashes link reports; repetition alone does not establish wrongdoing.').waitFor();
      });
      try {
        await page.goto('/#/map');
        await page.getByRole('button', { name: 'Sign out' }).click();
        await h1('Institutional access');
      } catch (error) { warn(`Sign out failed: ${error.message}`); }
      for (const [name, code] of [['15-hindi', 'hi'], ['16-marathi', 'mr']]) {
        await step(name, async () => {
          await page.goto(bangkok);
          await setLang(code);
          await page.waitForFunction(c => localStorage.getItem('saavdhan.lang') === c && document.documentElement.lang === c, code);
          await page.locator('.verdict-strip--STOP').waitFor();
        });
      }
      await setLang('en');
      if (!checkinRoute) warn('Check-in route not reached.');
    } finally {
      await context.close();
    }
  }
} finally {
  await browser.close();
}

const failures = results.filter(result => result.error);
assert.equal(results.length, STEPS * 2, 'Expected one result per step and viewport.');
const lines = [
  '# App screenshots', '',
  'All screenshots use synthetic demo data generated by the app; no real people, numbers or agencies.', '',
  'Mobile: 390 × 844 CSS pixels, device scale factor 2. Desktop: 1366 × 900 CSS pixels, device scale factor 1. Full-page captures extend beyond the viewport (the mobile tab bar is fixed, so it appears mid-page in full-page images). Oversized PNGs are recaptured at CSS pixel scale.', '',
  ...results.filter(result => !result.error).map(result => `- [${result.filename}](${result.filename}) — ${descriptions[result.filename.replace(/-(mobile|desktop)\.png$/, '')]} ${result.bytes.toLocaleString('en-IN')} bytes; ${result.width} × ${result.height} pixels; ${result.scale} scale.`), '',
  '## Capture', '',
  'Build the frontend and start an isolated local backend with model extraction disabled, an empty API key, a new temporary data directory, and the demo officer password used by the script. The backend serves the built frontend. Do not reuse a data directory containing personal information.', '',
  'From the repository root (PowerShell):', '',
  '```powershell',
  'npm --prefix tools/screenshots ci',
  'npm --prefix tools/screenshots exec -- playwright install chromium',
  "$env:BASE_URL = 'http://localhost:8123'; node tools/screenshots/capture.mjs", '```', '',
  'The script permits localhost addresses only, walks the story in a fresh browser context per viewport (home → Bangkok demo → review → STOP → evidence and ZIP → check-in plan → check-in → missed → family alert → help; Dubai demo → VERIFY FIRST; officer login → map → pattern), logs each step, and continues after failures. The map uses bundled district boundaries only; no background tiles are requested. No external account login is used.', '',
  `Capture result: ${results.length - failures.length}/${STEPS * 2} images captured.`,
  '',
  ...failures.map(result => `- Failed ${result.filename}: ${result.error.replace(/\s+/g, ' ')}`),
  ...warnings.map(message => `- Warning: ${message}`), '',
];
await writeFile(new URL('README.md', output), lines.join('\n'));
await writeFile(new URL('capture-results.json', output), `${JSON.stringify({ results, warnings }, null, 2)}\n`);
if (failures.length) process.exitCode = 1;
