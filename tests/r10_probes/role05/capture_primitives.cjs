// Paint only fixed local controls; never interpret inspector metadata as a paint verdict.
const fs = require('node:fs/promises');
const path = require('node:path');
const { createRequire } = require('node:module');
const deps = createRequire(path.resolve(process.env.DEEPVIZ_NODE_DEPS_ROOT || '.', 'package.json'));
const { chromium } = deps('playwright');

async function capture() {
  if (!process.argv[2]) throw new Error('Usage: node capture_primitives.cjs NEW_OUTPUT_DIRECTORY');
  const out = path.resolve(process.argv[2]);
  await fs.mkdir(out); // Refuse to overwrite a previous capture.
  const cases = JSON.parse(await fs.readFile(path.join(__dirname, 'cases.json'), 'utf8'));
  const browser = await chromium.launch({ headless: true, args: ['--disable-background-networking'] });
  const report = { playwright: deps('playwright/package.json').version, chromium: browser.version(), cases: [] };
  try {
    for (const fixture of cases) {
      const page = await browser.newPage({ viewport: { width: 100, height: 100 }, deviceScaleFactor: 1 });
      const consoleErrors = [];
      const requests = [];
      page.on('console', message => { if (message.type() === 'error') consoleErrors.push(message.text()); });
      page.on('pageerror', error => consoleErrors.push(String(error)));
      page.on('request', request => requests.push(request.url()));
      await page.route('**/*', route => route.abort());
      const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 64 64">${fixture.geometry}</svg>`;
      await fs.writeFile(path.join(out, `${fixture.name}.svg`), svg, 'utf8');
      await page.setContent(`<html><head><style>body{margin:0;background:white}svg{display:block}</style></head><body>${svg}</body></html>`);
      await page.locator('svg').screenshot({ path: path.join(out, `${fixture.name}.png`), animations: 'disabled' });
      const bbox = await page.locator('svg').evaluate(element => {
        const box = element.getBBox();
        return { x: box.x, y: box.y, width: box.width, height: box.height };
      });
      report.cases.push({ name: fixture.name, expected_visible: fixture.visible, bbox, console_errors: consoleErrors, requests });
      await page.close();
    }
    await fs.writeFile(path.join(out, 'browser.json'), `${JSON.stringify(report, null, 2)}\n`);
    console.log(JSON.stringify(report, null, 2));
  } finally {
    await browser.close();
  }
}

capture().catch(error => { console.error(error); process.exitCode = 1; });
