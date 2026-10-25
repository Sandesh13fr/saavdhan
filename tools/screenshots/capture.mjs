import assert from 'node:assert/strict';
import { mkdir, readFile, stat, writeFile } from 'node:fs/promises';
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
  '01-check': 'Check offer home screen and built-in synthetic demo offers.',
  '02-verdict-stop': 'Bangkok demo STOP verdict, recruiter-list status, rules and extracted facts.',
  '03-rule-quote': 'First Bangkok rule card with its verbatim offer quote and source.',
  '04-near-miss': 'Dubai near-miss demo: VERIFY_FIRST verdict and points to check before paying.',
  '05-checkin-plan': 'Saved synthetic traveller/contact aliases and travel plan, showing On schedule.',
  '06-missed': 'Check-in missed after three presses of the demo clock button.',
  '07-family': 'Simulated family phone displaying the missed check-in alert.',
  '08-map': 'Synthetic Maharashtra report map with the first repeated agent hash highlighting districts.',
  '09-hindi': 'Bangkok demo verdict in Hindi.',
  '10-marathi': 'Bangkok demo verdict in Marathi.',
  '11-limits': 'Limits, recruiter-list status, rule sources and official contact information.',
};

await mkdir(output, { recursive: true });
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
    let bangkokRoute;
    const warn = message => {
      if (warnings.includes(`${viewport.name}: ${message}`)) return;
      warnings.push(`${viewport.name}: ${message}`);
      console.warn(`WARN ${viewport.name}: ${message}`);
    };
    const tab = name => page.getByRole('navigation', { name: 'Main' }).getByRole('link', { name, exact: true });
    const english = () => page.getByRole('button', { name: 'EN', exact: true }).click();
    const checkListDate = async () => {
      const bannerDate = await page.locator('.banner-date').innerText();
      if (!/\d{4}-\d{2}-\d{2}/.test(bannerDate)) warn(`Recruiter-list date unavailable in the app: ${bannerDate}`);
    };
    const bangkok = async () => {
      await english();
      if (bangkokRoute) {
        await page.goto(bangkokRoute);
      } else {
        await tab('Check offer').click();
        await page.getByRole('button', { name: /Bangkok/ }).click();
      }
      await page.locator('.banner-STOP').waitFor();
      await page.getByRole('heading', { name: 'Stop. Do not pay or travel yet.', exact: true }).waitFor();
      await checkListDate();
      bangkokRoute = page.url();
    };
    const capture = async (name, target = page, fullPage = true) => {
      await page.evaluate(() => document.fonts.ready);
      assert(!/\bsafe\b/i.test(await page.locator('body').innerText()), 'Unexpected verdict wording.');
      if (target === page) await page.evaluate(() => window.scrollTo(0, 0));
      const filename = `${name}-${viewport.name}.png`;
      const path = fileURLToPath(new URL(filename, output));
      const options = { path, type: 'png', animations: 'disabled', ...(target === page ? { fullPage } : {}) };
      await target.screenshot(options);
      let scale = 'device';
      if ((await stat(path)).size >= maxBytes) {
        await target.screenshot({ ...options, scale: 'css' });
        scale = 'css';
      }
      const bytes = await readFile(path);
      assert(bytes.subarray(0, 8).equals(Buffer.from([137, 80, 78, 71, 13, 10, 26, 10])), 'Invalid PNG.');
      assert(bytes.length > 100 && bytes.length < maxBytes, `PNG size out of bounds: ${bytes.length}`);
      const result = {
        filename, bytes: bytes.length, width: bytes.readUInt32BE(16), height: bytes.readUInt32BE(20), scale,
      };
      results.push(result);
      console.log(`OK ${filename}: ${result.bytes} bytes (${result.width}x${result.height}, ${scale} scale)`);
    };
    const step = async (name, action) => {
      try {
        await action();
      } catch (error) {
        const reason = error.message;
        results.push({ filename: `${name}-${viewport.name}.png`, error: reason });
        console.error(`FAIL ${name}-${viewport.name}: ${reason}`);
      }
    };
    try {
      await step('01-check', async () => {
        await page.goto('/');
        await page.getByRole('heading', { name: 'Check your job offer', exact: true }).waitFor();
        await page.getByRole('button', { name: /Bangkok/ }).waitFor();
        await capture('01-check');
      });
      await step('02-verdict-stop', async () => {
        await bangkok();
        await capture('02-verdict-stop');
      });
      await step('03-rule-quote', async () => {
        await bangkok();
        const card = page.getByRole('listitem').filter({ has: page.getByRole('blockquote') }).first();
        await card.evaluate(element => element.scrollIntoView({ block: 'center' }));
        await capture('03-rule-quote', card);
      });
      await step('04-near-miss', async () => {
        await english();
        await tab('Check offer').click();
        await page.getByRole('button', { name: /Dubai/ }).click();
        await page.locator('.banner-VERIFY_FIRST').waitFor();
        await page.getByRole('heading', { name: 'Check these points before you pay.', exact: true }).waitFor();
        await checkListDate();
        await capture('04-near-miss');
      });
      await step('05-checkin-plan', async () => {
        await bangkok();
        await page.getByRole('button', { name: /check-in plan/ }).click();
        await page.getByLabel('Your alias (not your real name)', { exact: true }).fill('Student (demo)');
        await page.getByRole('textbox', { name: 'Contact alias', exact: true }).first().fill('Brother (demo)');
        await page.getByLabel('How to reach them', { exact: true }).first().fill('SMS (simulated)');
        await page.getByLabel('Travel plan', { exact: true }).fill('Pune -> Bangkok (demo)');
        await page.getByRole('button', { name: 'Save plan', exact: true }).click();
        await page.getByRole('heading', { name: 'On schedule', exact: true }).waitFor();
        await capture('05-checkin-plan');
      });
      await step('06-missed', async () => {
        await english();
        await tab('Check-in plan').click();
        const clock = page.getByRole('button', { name: /move the clock/ });
        for (let i = 0; i < 3; i++) {
          const response = page.waitForResponse(r => r.url().endsWith('/api/demo/advance-clock') && r.request().method() === 'POST');
          await clock.click();
          assert((await response).ok(), 'Demo clock request failed.');
          await page.waitForFunction(() => !document.querySelector('form[aria-busy="true"]'), null, { timeout });
        }
        await page.getByRole('heading', { name: 'Check-in missed', exact: true }).waitFor();
        await capture('06-missed');
      });
      await step('07-family', async () => {
        await english();
        await tab('Family').click();
        await page.getByRole('region', { name: 'Family alerts', exact: true }).waitFor();
        await page.getByRole('heading', { name: 'Missed check-in alert', exact: true }).first().waitFor();
        await page.getByText(/Simulated alert: Student \(demo\) missed a check-in/).first().waitFor();
        await capture('07-family');
      });
      await step('08-map', async () => {
        await english();
        await tab('Map').click();
        try {
          await page.getByLabel('Email', { exact: true }).fill('officer@saavdhan.example');
          await page.getByLabel('Password', { exact: true }).fill('screenshot-officer-pw-2026');
          await page.getByRole('button', { name: 'Sign in', exact: true }).click();
          await page.waitForFunction(() => document.querySelectorAll('path.leaflet-interactive').length > 0, null, { timeout });
          try {
            await page.waitForLoadState('networkidle', { timeout: 15_000 });
          } catch {
            warn('Map network did not become idle within 15 seconds; checking visible tiles directly.');
          }
          await page.waitForFunction(() => {
            const tiles = [...document.querySelectorAll('.leaflet-tile-container img.leaflet-tile')];
            return tiles.length > 0 && tiles.every(tile => tile.complete && tile.naturalWidth > 0);
          }, null, { timeout: 15_000 });
          const agent = page.getByRole('complementary', { name: 'Agents seen in several reports' })
            .getByRole('button').first();
          await agent.click();
          await page.getByText(/^Highlighted districts:/).waitFor();
          assert.equal(await agent.getAttribute('aria-pressed'), 'true');
          assert(await page.locator('path.leaflet-interactive[stroke="#9a3412"]').count() > 0, 'No districts highlighted.');
          await capture('08-map');
        } finally {
          const signOut = page.getByRole('button', { name: 'Sign out', exact: true });
          if (await signOut.isVisible()) {
            const loggedOut = page.waitForResponse(r => r.url().endsWith('/api/auth/logout') && r.request().method() === 'POST');
            await signOut.click();
            assert((await loggedOut).ok(), 'Local officer logout failed.');
            await page.getByRole('button', { name: 'Sign in', exact: true }).waitFor();
          }
        }
      });
      for (const [name, language] of [['09-hindi', 'हिंदी'], ['10-marathi', 'मराठी']]) {
        await step(name, async () => {
          await bangkok();
          await page.getByTitle(language, { exact: true }).click();
          await page.waitForFunction(code => localStorage.getItem('saavdhan.lang') === code, name === '09-hindi' ? 'hi' : 'mr', { timeout });
          await page.locator('.banner-STOP').waitFor();
          await capture(name);
        });
      }
      await step('11-limits', async () => {
        await english();
        await tab('Limits').click();
        await page.getByRole('heading', { name: 'What Saavdhan can and cannot do', exact: true }).waitFor();
        await page.getByText('R1_TOURIST_VISA', { exact: true }).waitFor();
        const missingCopy = (await page.locator('main').innerText()).match(/\blimits\.[a-z_]+\b/g);
        if (missingCopy) warn(`Untranslated app copy on Limits: ${[...new Set(missingCopy)].join(', ')}`);
        await capture('11-limits');
      });
    } finally {
      await context.close();
    }
  }
} finally {
  await browser.close();
}

const failures = results.filter(result => result.error);
assert.equal(results.length, 22, 'Expected one result per step and viewport.');
const lines = [
  '# App screenshots', '',
  'All screenshots use synthetic demo data generated by the app; no real people, numbers or agencies.', '',
  'Mobile: 390 × 844 CSS pixels, device scale factor 2. Desktop: 1366 × 900 CSS pixels, device scale factor 1. Full-page captures extend beyond the viewport; rule cards are element captures. Oversized PNGs are recaptured at CSS pixel scale.', '',
  ...results.filter(result => !result.error).map(result => `- [${result.filename}](${result.filename}) — ${descriptions[result.filename.replace(/-(mobile|desktop)\.png$/, '')]} ${result.bytes.toLocaleString('en-IN')} bytes; ${result.width} × ${result.height} pixels; ${result.scale} scale.`), '',
  '## Capture', '',
  'Build the frontend and start an isolated local backend with model extraction disabled, an empty API key, a new temporary data directory, and the demo officer password used by the script. The backend serves the built frontend. Do not reuse a data directory containing personal information.', '',
  'From the repository root (PowerShell):', '',
  '```powershell',
  'npm --prefix tools/screenshots ci',
  'npm --prefix tools/screenshots exec -- playwright install chromium',
  "$env:BASE_URL = 'http://localhost:8123'; node tools/screenshots/capture.mjs", '```', '',
  'The script permits localhost addresses only, uses a fresh browser context per viewport, logs each step, and continues after failures. Map boundaries are bundled app assets; background tiles come from OpenStreetMap. No external account login is used.', '',
  `Capture result: ${results.length - failures.length}/22 images captured.`,
  '',
  ...failures.map(result => `- Failed ${result.filename}: ${result.error.replace(/\s+/g, ' ')}`),
  ...warnings.map(message => `- Warning: ${message}`), '',
];
await writeFile(new URL('README.md', output), lines.join('\n'));
await writeFile(new URL('capture-results.json', output), `${JSON.stringify({ results, warnings }, null, 2)}\n`);
if (failures.length) process.exitCode = 1;
