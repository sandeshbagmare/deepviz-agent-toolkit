// Optional real-browser supplement; use installed Playwright, never install here.
const fs = require('node:fs');
const http = require('node:http');
const path = require('node:path');
const { chromium } = require('playwright');

const root = path.resolve(process.argv[2] || '');
const summary = JSON.parse(fs.readFileSync(path.join(root, 'summary.json'), 'utf8'));
const expected = [summary.parent_title, ...summary.child_titles];
const contentTypes = { '.html': 'text/html; charset=utf-8', '.svg': 'image/svg+xml' };

(async () => {
  const server = http.createServer((request, response) => {
    if (request.url === '/favicon.ico') { response.writeHead(204); response.end(); return; }
    const filename = path.resolve(root, '.' + decodeURIComponent(new URL(request.url, 'http://localhost').pathname));
    if (!filename.startsWith(root + path.sep)) { response.writeHead(403); response.end(); return; }
    try {
      const content = fs.readFileSync(filename);
      response.writeHead(200, { 'Content-Type': contentTypes[path.extname(filename)] || 'application/octet-stream' });
      response.end(content);
    } catch { response.writeHead(404); response.end(); }
  });
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  let browser;
  const results = [];
  try {
    const channel = process.env.DEEPVIZ_BROWSER_CHANNEL || (process.platform === 'win32' ? 'msedge' : undefined);
    browser = await chromium.launch({ channel, headless: true });
    const origin = `http://127.0.0.1:${server.address().port}`;
    for (const [name, files] of Object.entries(summary.artifacts)) {
      for (const extension of ['html', 'svg']) {
        const page = await browser.newPage({ viewport: { width: 1100, height: 800 } });
        const errors = [], warnings = [], pageErrors = [], failedRequests = [], externalRequests = [];
        page.on('console', message => {
          if (message.type() === 'error') errors.push(message.text());
          if (message.type() === 'warning') warnings.push(message.text());
        });
        page.on('pageerror', error => pageErrors.push(error.message));
        page.on('requestfailed', request => failedRequests.push(request.url()));
        page.on('request', request => { if (!request.url().startsWith(origin)) externalRequests.push(request.url()); });
        const response = await page.goto(origin + '/' + files[extension].replaceAll('\\', '/'), { waitUntil: 'load' });
        if (extension === 'html') await page.waitForFunction(() => [...document.images].every(image => image.complete && image.naturalWidth > 0));
        const state = await page.evaluate(titles => ({
          title: document.title,
          h1: document.querySelector('h1')?.textContent,
          h2: [...document.querySelectorAll('h2')].map(node => node.textContent),
          xssMarkerType: typeof window.__DV_XSS__,
          executableElements: document.querySelectorAll('script,iframe,object,embed,foreignObject').length,
          anchors: document.querySelectorAll('a[href]').length,
          eventAttributes: [...document.querySelectorAll('*')].flatMap(node => [...node.attributes]
            .filter(attribute => attribute.name.toLowerCase().startsWith('on')).map(attribute => attribute.name)),
          images: [...document.images].map(image => ({ src: image.getAttribute('src'), width: image.naturalWidth, height: image.naturalHeight })),
          requiredSvgTitles: titles.map(title => {
            const node = [...document.querySelectorAll('svg text')].find(item => item.textContent === title);
            if (!node) return { title, exists: false };
            const box = node.getBoundingClientRect();
            const style = getComputedStyle(node);
            return { title, exists: true, width: box.width, height: box.height,
              display: style.display, visibility: style.visibility, opacity: style.opacity };
          }),
          bars: document.querySelectorAll('[aria-roledescription="bar"]').length,
          points: document.querySelectorAll('[aria-roledescription="point"]').length,
        }), expected);
        const titlesCorrect = extension === 'html'
          ? state.title === expected[0] && state.h1 === expected[0] && JSON.stringify(state.h2) === JSON.stringify(expected.slice(1))
          : state.requiredSvgTitles.every(title => title.exists && title.width > 0 && title.height > 0
            && title.display !== 'none' && title.visibility === 'visible' && Number(title.opacity) > 0);
        const geometryCorrect = extension === 'html'
          ? state.images.length === 1 && state.images[0].src === 'chart.svg' && state.images[0].width === 640 && state.images[0].height === 400
          : state.bars === (name === 'ordinary' ? 3 : 1) && state.points === (name === 'ordinary' ? 3 : 1);
        const screenshot = extension === 'html' ? `${name}-browser.png` : null;
        if (screenshot) await page.screenshot({ path: path.join(root, screenshot), fullPage: true });
        const pass = response.status() === 200 && titlesCorrect && geometryCorrect && !errors.length && !pageErrors.length
          && !failedRequests.length && !externalRequests.length && state.xssMarkerType === 'undefined'
          && !state.executableElements && !state.eventAttributes.length && !state.anchors;
        results.push({ name, extension, status: response.status(), titlesCorrect, geometryCorrect,
          screenshot, pass, errors, warnings, pageErrors, failedRequests, externalRequests, state });
        fs.writeFileSync(path.join(root, 'browser-partial.json'), JSON.stringify(results, null, 2));
        await page.close();
      }
    }
    const result = { source_sha: summary.source_sha, node: process.version,
      playwright: require('playwright/package.json').version, browser: browser.version(),
      renderer: 'Native Vega-Lite compiled SVG painted by Edge; no CDN or engine fallback',
      favicon: 'ephemeral harness HTTP204', directSvgScreenshot: 'not attempted; wrapper image and converter PNG inspected', results };
    fs.writeFileSync(path.join(root, 'browser-results.json'), JSON.stringify(result, null, 2));
    console.log(JSON.stringify({ navigations: results.length, passed: results.filter(result => result.pass).length,
      consoleErrors: results.reduce((sum, result) => sum + result.errors.length, 0) }));
    if (results.some(result => !result.pass)) process.exitCode = 1;
  } finally {
    if (browser) await browser.close();
    await new Promise(resolve => server.close(resolve));
  }
})().catch(error => { console.error(error.message); process.exitCode = 1; });
