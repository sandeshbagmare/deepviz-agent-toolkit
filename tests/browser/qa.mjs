import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { mkdir, readFile, realpath, writeFile } from 'node:fs/promises';
import { createRequire } from 'node:module';
import path from 'node:path';
import { pathToFileURL } from 'node:url';

export const CANARY = 'DEEPVIZ_QA_32635';
export const PAYLOAD = `</script><script>globalThis.__deepviz_xss=1</script><img data-deepviz-xss src="https://qa.invalid/${CANARY}" onerror="globalThis.__deepviz_xss=1">`;
const ORIGIN = 'https://artifacts.deepviz.invalid';
const VIEWPORT = { width: 1280, height: 960 };
const MAX_DIFF = 0.005;
const REGION_MAX_DIFF = 0.001;
const sha256 = value => createHash('sha256').update(value).digest('hex');

export function validateManifest(manifest) {
  assert.equal(manifest?.version, 1, 'Manifest version must be 1');
  assert.match(manifest.sourceCommit ?? '', /^[0-9a-f]{40}$/, 'sourceCommit must be a full git SHA');
  assert.ok(Array.isArray(manifest.cases) && manifest.cases.length, 'Manifest needs cases');
  const seen = new Set();
  for (const item of manifest.cases) {
    assert.match(item.id ?? '', /^[a-z0-9][a-z0-9-]{0,95}$/, 'Invalid case ID');
    assert.ok(!seen.has(item.id), `Duplicate case ID: ${item.id}`);
    seen.add(item.id);
    assert.ok(['plotly', 'echarts', 'antv', 'vega', 'matplotlib'].includes(item.engine), 'Unknown engine');
    assert.ok(['html', 'svg', 'png'].includes(item.format), 'Unknown artifact format');
    assert.ok(typeof item.path === 'string' && item.path.length > 0 &&
      !/[:\\?#\x00]/.test(item.path) && !item.path.startsWith('/') &&
      item.path.split('/').every(part => part && part !== '.' && part !== '..') &&
      item.path.endsWith(`.${item.format}`), 'Use a relative artifact path with its real extension');
    assert.ok(typeof item.title === 'string' && item.title.length, 'Expected title is required');
    for (const flag of ['dashboard', 'security']) {
      assert.ok(item[flag] === undefined || typeof item[flag] === 'boolean', `Invalid ${flag}`);
    }
    if (item.format === 'html') {
      assert.ok(Array.isArray(item.labels) && item.labels.length && item.labels.every(v => typeof v === 'string' && v),
        'HTML requires expected category labels');
      assert.ok(Array.isArray(item.numbers) && new Set(item.numbers).size >= 2 &&
        item.numbers.every(v => typeof v === 'string' && /^-?\d+(?:\.\d+)?$/.test(v)),
      'HTML requires at least two numeric axis-label expectations');
      assert.ok(Array.isArray(item.regions) && item.regions.length, 'HTML requires visible chart regions');
      if (item.dashboard) assert.ok(item.regions.length >= 2, 'Dashboard requires two regions');
      assert.equal(new Set(item.regions.map(region => `${region.frame ?? ''}\n${region.selector}`)).size,
        item.regions.length, 'Chart regions must be distinct');
      for (const region of item.regions) {
        assert.ok(typeof region.selector === 'string' && region.selector, 'Each region requires a CSS selector');
        assert.ok(region.frame === undefined || (typeof region.frame === 'string' && region.frame), 'Invalid frame selector');
        assert.ok(region.minMarks === undefined || (Number.isInteger(region.minMarks) && region.minMarks > 0), 'Invalid mark count');
      }
    }
  }
  return manifest;
}

export function validateCoverage(cases) {
  const has = predicate => assert.ok(cases.some(predicate), 'Acceptance coverage is incomplete');
  for (const engine of ['plotly', 'echarts', 'antv']) {
    for (const security of [false, true]) has(item => item.engine === engine && item.format === 'html' &&
      Boolean(item.security) === security && !item.dashboard);
  }
  for (const security of [false, true]) has(item => item.dashboard && item.format === 'html' &&
    Boolean(item.security) === security && item.regions?.length >= 2);
  for (const engine of ['vega', 'matplotlib']) has(item => item.engine === engine && ['svg', 'png'].includes(item.format));
}

export function cdnEntries(name, version, localPath, assetPath) {
  assert.match(version, /^\d+\.\d+\.\d+(?:-[\w.-]+)?$/, 'A CDN route needs exact semver');
  const urls = [
    `https://cdn.jsdelivr.net/npm/${name}@${version}/${assetPath}`,
    `https://unpkg.com/${name}@${version}/${assetPath}`,
  ];
  if (name === 'plotly.js-dist-min') urls.push(`https://cdn.plot.ly/plotly-${version}.min.js`);
  return urls.map(url => ({ url, name, version, localPath }));
}

// Self-contained so Playwright can run the same pixel logic in its browser context.
export async function analyzeRaster(input) {
  async function decode(base64) {
    const image = new Image();
    image.src = `data:image/png;base64,${base64}`;
    await image.decode();
    const canvas = document.createElement('canvas');
    canvas.width = image.naturalWidth;
    canvas.height = image.naturalHeight;
    const context = canvas.getContext('2d', { willReadFrequently: true });
    context.drawImage(image, 0, 0);
    return { rgba: context.getImageData(0, 0, canvas.width, canvas.height).data,
      width: canvas.width, height: canvas.height };
  }
  const current = input.png ? await decode(input.png) : input;
  const baseline = input.baselinePng ? await decode(input.baselinePng) :
    input.baselineRgba ? { rgba: input.baselineRgba, width: input.baselineWidth, height: input.baselineHeight } : null;
  const { rgba, width, height } = current;
  const buckets = new Set();
  const tiles = new Map();
  const coloredMask = new Uint8Array(width * height);
  let inkPixels = 0;
  let coloredPixels = 0;
  let solidColoredPixels = 0;
  let changedPixels = 0;
  let maxDelta = 0;
  const dimensionsMatch = !baseline || (width === baseline.width && height === baseline.height);
  for (let offset = 0; offset < rgba.length; offset += 4) {
    const alpha = rgba[offset + 3] / 255;
    const rgb = [0, 1, 2].map(channel => Math.round(rgba[offset + channel] * alpha + 255 * (1 - alpha)));
    if (Math.min(...rgb) < 240) inkPixels++;
    if (Math.max(...rgb) - Math.min(...rgb) > 24 && Math.min(...rgb) < 235) {
      coloredPixels++;
      buckets.add(rgb.map(channel => Math.floor(channel / 32)).join(','));
      const pixel = offset / 4;
      coloredMask[pixel] = 1;
      const tile = `${Math.floor((pixel % width) / width * 16)},${Math.floor(Math.floor(pixel / width) / height * 12)}`;
      tiles.set(tile, (tiles.get(tile) ?? 0) + 1);
      // Font-edge color fringes are not filled chart marks.
      if (pixel % width > 0 && pixel % width < width - 1 && pixel >= width && pixel < width * (height - 1) &&
        [-4, 4, -width * 4, width * 4].every(step => [0, 1, 2].every(channel =>
          Math.abs(rgba[offset + step + channel] - rgb[channel]) < 12))) solidColoredPixels++;
    }
    if (baseline && dimensionsMatch) {
      const delta = Math.max(...[0, 1, 2, 3].map(channel => Math.abs(rgba[offset + channel] - baseline.rgba[offset + channel])));
      maxDelta = Math.max(maxDelta, delta);
      if (delta > 16) changedPixels++;
    }
  }
  const queue = new Int32Array(width * height);
  let largestColoredComponentPixels = 0;
  let largestColoredComponentSpan = 0;
  for (let start = 0; start < coloredMask.length; start++) {
    if (!coloredMask[start]) continue;
    coloredMask[start] = 0;
    let head = 0;
    let tail = 1;
    queue[0] = start;
    let minX = width;
    let maxX = 0;
    let minY = height;
    let maxY = 0;
    while (head < tail) {
      const pixel = queue[head++];
      const x = pixel % width;
      const y = Math.floor(pixel / width);
      minX = Math.min(minX, x); maxX = Math.max(maxX, x);
      minY = Math.min(minY, y); maxY = Math.max(maxY, y);
      for (let dy = -1; dy <= 1; dy++) for (let dx = -1; dx <= 1; dx++) {
        const nx = x + dx;
        const ny = y + dy;
        const neighbor = ny * width + nx;
        if (nx >= 0 && nx < width && ny >= 0 && ny < height && coloredMask[neighbor]) {
          coloredMask[neighbor] = 0;
          queue[tail++] = neighbor;
        }
      }
    }
    if (tail > largestColoredComponentPixels) {
      largestColoredComponentPixels = tail;
      largestColoredComponentSpan = Math.max((maxX - minX + 1) / width, (maxY - minY + 1) / height);
    }
  }
  return { width, height, inkPixels, coloredPixels, solidColoredPixels,
    largestColoredComponentPixels, largestColoredComponentSpan, colorBuckets: buckets.size,
    activeTiles: [...tiles.values()].filter(count => count >= 4).length,
    ...(baseline ? { dimensionsMatch, changedPixels, maxDelta,
      diffRatio: dimensionsMatch ? changedPixels / (width * height) : 1 } : {}) };
}

export function playwrightFrom(depsRoot) {
  const require = createRequire(path.join(path.resolve(depsRoot), 'package.json'));
  return { chromium: require('playwright').chromium, version: require('playwright/package.json').version };
}

export async function loadCdnAssets(depsRoot) {
  const require = createRequire(path.join(path.resolve(depsRoot), 'package.json'));
  const assets = new Map();
  const definitions = [
    ['plotly.js-dist-min', 'plotly.min.js'], ['echarts', 'dist/echarts.min.js'],
    ['@antv/g2', 'dist/g2.min.js'], ['vega', 'build/vega.min.js'],
    ['vega-lite', 'build/vega-lite.min.js'], ['vega-embed', 'build/vega-embed.min.js'],
  ];
  for (const [name, assetPath] of definitions) {
    let directory = path.dirname(require.resolve(name));
    let metadata;
    while (true) {
      try {
        const candidate = JSON.parse(await readFile(path.join(directory, 'package.json'), 'utf8'));
        if (candidate.name === name) { metadata = candidate; break; }
      } catch (error) { if (error.code !== 'ENOENT') throw error; }
      const parent = path.dirname(directory);
      assert.notEqual(parent, directory, `Cannot find package metadata for ${name}`);
      directory = parent;
    }
    const localPath = path.join(directory, assetPath);
    const body = await readFile(localPath);
    for (const entry of cdnEntries(name, metadata.version, localPath, assetPath)) {
      assets.set(entry.url, { ...entry, body, sha256: sha256(body) });
    }
  }
  return assets;
}

function browserInstrumentation() {
  globalThis.__deepviz_xss = 0;
  globalThis.__deepviz_qa_text = [];
  let seed = 32635;
  Math.random = () => { seed = (1664525 * seed + 1013904223) >>> 0; return seed / 4294967296; };
  for (const type of [globalThis.CanvasRenderingContext2D, globalThis.OffscreenCanvasRenderingContext2D]) {
    if (!type) continue;
    for (const name of ['fillText', 'strokeText']) {
      const original = type.prototype[name];
      type.prototype[name] = function (...args) {
        if (Number.isFinite(args[1]) && Number.isFinite(args[2]) && globalThis.__deepviz_qa_text.length < 10000) {
          globalThis.__deepviz_qa_text.push(String(args[0]));
        }
        return Reflect.apply(original, this, args);
      };
    }
  }
}

function visibleTextAndSecurity() {
  const drawn = [...document.querySelectorAll('svg text')].filter(element => {
    const rect = element.getBoundingClientRect();
    const style = getComputedStyle(element);
    return rect.width > 0 && rect.height > 0 && style.visibility !== 'hidden' && style.display !== 'none';
  }).map(element => element.textContent);
  return {
    text: [document.body?.innerText ?? '', ...drawn, ...(globalThis.__deepviz_qa_text ?? [])].join('\n'),
    drawn: [...drawn, ...(globalThis.__deepviz_qa_text ?? [])],
    xss: globalThis.__deepviz_xss,
    injectedElements: document.querySelectorAll('[data-deepviz-xss]').length,
  };
}

async function stableScreenshot(page) {
  let previous;
  let identical = 0;
  for (let attempt = 0; attempt < 60; attempt++) {
    const png = await page.screenshot({ fullPage: true, animations: 'disabled' });
    const hash = sha256(png);
    identical = hash === previous ? identical + 1 : 0;
    if (identical >= 3) return png;
    previous = hash;
    await page.waitForTimeout(100);
  }
  throw new Error('Chart never reached three stable screenshot intervals');
}

function assertMeaningful(metrics, label) {
  assert.ok(metrics.width >= 240 && metrics.height >= 200, `${label}: chart region is undersized`);
  assert.ok(metrics.inkPixels >= 500, `${label}: nearly empty output`);
  const coloredMarks = metrics.solidColoredPixels >= 150 ||
    (metrics.largestColoredComponentPixels >= 150 && metrics.largestColoredComponentSpan >= 0.15);
  assert.ok(coloredMarks && metrics.colorBuckets >= 1 && metrics.activeTiles >= 6 &&
    metrics.coloredPixels / (metrics.width * metrics.height) < 0.9,
    `${label}: missing meaningful colored chart marks (${JSON.stringify(metrics)})`);
}

export async function runArtifactSuite({ manifest, artifactRoot, browser, playwrightVersion,
  assets, baselineDir, outputDir, record = false, selfTest = false }) {
  validateManifest(manifest);
  if (!selfTest) validateCoverage(manifest.cases);
  const root = await realpath(artifactRoot);
  const artifacts = new Map();
  for (const item of manifest.cases) {
    const resolved = await realpath(path.resolve(root, item.path));
    const relative = path.relative(root, resolved);
    assert.ok(relative && !relative.startsWith('..') && !path.isAbsolute(relative), 'Artifact escaped its root');
    const body = await readFile(resolved);
    artifacts.set(new URL(item.path, `${ORIGIN}/`).href, { body, sha256: sha256(body), format: item.format });
  }
  await mkdir(path.dirname(outputDir), { recursive: true });
  await mkdir(outputDir); // Never overwrite another verification run.
  if (record) await mkdir(baselineDir, { recursive: true });
  const environment = { platform: process.platform, browser: browser.version(), playwright: playwrightVersion,
    viewport: VIEWPORT, deviceScaleFactor: 1, locale: 'en-US', timezoneId: 'UTC' };
  const report = { mode: selfTest ? 'harness-selftest' : record ? 'baseline-recording' : 'candidate-verification',
    sourceCommit: manifest.sourceCommit, environment, startedAt: new Date().toISOString(), cases: [] };
  for (const item of manifest.cases) {
    const result = { id: item.id, engine: item.engine, format: item.format, errors: [],
      consoleErrors: [], pageErrors: [], unexpectedRequests: [], fulfilledAssets: [], regions: [] };
    const context = await browser.newContext({ viewport: VIEWPORT, deviceScaleFactor: 1,
      locale: 'en-US', timezoneId: 'UTC', colorScheme: 'light', reducedMotion: 'reduce',
      serviceWorkers: 'block', acceptDownloads: false });
    let page;
    try {
      await context.addInitScript(browserInstrumentation);
      await context.setOffline(true);
      assert.equal(typeof context.routeWebSocket, 'function', 'Playwright with WebSocket routing is required');
      await context.routeWebSocket('**/*', socket => {
        result.unexpectedRequests.push(`WebSocket ${socket.url()}`);
        socket.close();
      });
      await context.route('**/*', async route => {
        const request = route.request();
        const url = request.url();
        const artifact = artifacts.get(url);
        const asset = assets.get(url);
        if (request.method() === 'GET' && artifact) {
          const types = { html: 'text/html; charset=utf-8', svg: 'image/svg+xml', png: 'image/png' };
          await route.fulfill({ status: 200, body: artifact.body, contentType: types[artifact.format] });
        } else if (request.method() === 'GET' && asset) {
          result.fulfilledAssets.push({ url, name: asset.name, version: asset.version, sha256: asset.sha256 });
          await route.fulfill({ status: 200, body: asset.body, contentType: 'text/javascript; charset=utf-8' });
        } else if (request.method() === 'GET' && url === `${ORIGIN}/favicon.ico`) {
          await route.fulfill({ status: 204, body: '' });
        } else {
          result.unexpectedRequests.push(`${request.method()} ${url}`);
          await route.abort('blockedbyclient');
        }
      });
      context.on('page', opened => {
        opened.on('popup', () => result.errors.push('Unexpected popup'));
        opened.on('console', message => {
          if (message.type() === 'error') result.consoleErrors.push(message.text());
        });
        opened.on('pageerror', error => result.pageErrors.push(error.message));
        opened.on('dialog', async dialog => {
          result.errors.push(`Unexpected ${dialog.type()} dialog: ${dialog.message()}`);
          await dialog.dismiss();
        });
        opened.on('download', () => result.errors.push('Unexpected download'));
      });
      page = await context.newPage();
      page.setDefaultTimeout(12000);
      const url = new URL(item.path, `${ORIGIN}/`).href;
      const artifact = artifacts.get(url);
      result.artifactSha256 = artifact.sha256;
      if (item.security) {
        assert.ok(artifact.body.includes(Buffer.from(CANARY)) && artifact.body.includes(Buffer.from('__deepviz_xss')),
          'Security artifact does not contain the agreed hostile-input canary');
      }
      await page.goto(url, { waitUntil: 'load', timeout: 20000 });
      const regions = item.format === 'html' ? item.regions : [{ selector: item.format === 'svg' ? 'svg' : 'img' }];
      const locators = [];
      for (const region of regions) {
        const locator = region.frame ? page.frameLocator(region.frame).locator(region.selector) : page.locator(region.selector);
        assert.equal(await locator.count(), 1, `Ambiguous or missing chart region: ${region.selector}`);
        await locator.waitFor({ state: 'visible' });
        locators.push(locator);
      }
      const size = await page.evaluate(() => ({ width: document.documentElement.scrollWidth, height: document.documentElement.scrollHeight }));
      assert.ok(size.width <= 4096 && size.height <= 10000, 'Artifact is too large for bounded screenshot inspection');
      const fullScreenshot = await stableScreenshot(page);
      const analyzer = await context.newPage();
      const regionPngs = [];
      for (let index = 0; index < locators.length; index++) {
        const locator = locators[index];
        const png = await locator.screenshot({ animations: 'disabled' });
        regionPngs.push(png);
        const metrics = await analyzer.evaluate(analyzeRaster, { png: png.toString('base64') });
        assertMeaningful(metrics, `Region ${index}`);
        const structure = item.format === 'html' ? await locator.evaluate(element => ({
          canvases: element.querySelectorAll('canvas').length + Number(element.tagName.toLowerCase() === 'canvas'),
          marks: [...element.querySelectorAll('path,rect,circle,ellipse,polygon,polyline,line')].filter(mark => {
            const box = mark.getBoundingClientRect();
            const style = getComputedStyle(mark);
            return box.width > 0 && box.height > 0 && style.display !== 'none' && style.visibility !== 'hidden' &&
              Number(style.opacity) > 0 && (style.fill !== 'none' || style.stroke !== 'none');
          }).length,
        })) : {};
        if (item.format === 'html') assert.ok(structure.canvases > 0 || structure.marks >= (regions[index].minMarks ?? 1),
          `Region ${index}: no native canvas/SVG chart marks`);
        result.regions.push({ ...metrics, ...structure });
        await writeFile(path.join(outputDir, `${item.id}-region-${index}.png`), png);
      }
      await analyzer.close();
      const observations = [];
      for (const frame of page.frames()) observations.push(await frame.evaluate(visibleTextAndSecurity));
      for (const observation of observations) {
        assert.equal(observation.xss, 0, 'Hostile data executed a script');
        assert.equal(observation.injectedElements, 0, 'Hostile data became a real DOM element');
      }
      if (item.format === 'html') {
        const text = observations.map(observation => observation.text).join('\n').replace(/\s+/g, ' ');
        for (const expected of [item.title, ...item.labels]) assert.ok(text.includes(expected.replace(/\s+/g, ' ')),
          `Missing visible title/category text: ${expected}`);
        const numbers = new Set(observations.flatMap(observation => observation.drawn)
          .flatMap(text => String(text).match(/-?\d+(?:\.\d+)?/g) ?? []));
        for (const number of item.numbers) assert.ok(numbers.has(number), `Missing drawn numeric axis label: ${number}`);
        result.drawnNumbers = [...numbers];
        result.matchedTitle = item.title;
      } else {
        result.staticLabelCheck = 'Human baseline review required; raster checks do not perform OCR';
      }
      assert.equal(page.url(), url, 'Unexpected navigation');
      assert.deepEqual(result.consoleErrors, [], 'Browser console errors');
      assert.deepEqual(result.pageErrors, [], 'Uncaught page exceptions');
      assert.deepEqual(result.unexpectedRequests, [], 'Unexpected requests (all non-allowlisted traffic is blocked)');
      assert.deepEqual(result.errors, [], 'Unexpected browser side effects');
      const screenshot = item.format === 'html' ? fullScreenshot : await locators[0].screenshot({ animations: 'disabled' });
      await writeFile(path.join(outputDir, `${item.id}.png`), screenshot);
      const baselinePng = path.join(baselineDir, `${item.id}.png`);
      const baselineJson = path.join(baselineDir, `${item.id}.json`);
      const contract = sha256(JSON.stringify({ ...item, path: undefined }));
      if (record) {
        await writeFile(baselinePng, screenshot);
        for (let index = 0; index < regionPngs.length; index++) {
          await writeFile(path.join(baselineDir, `${item.id}-region-${index}.png`), regionPngs[index]);
        }
        await writeFile(baselineJson, JSON.stringify({ environment, contract,
          sourceCommit: manifest.sourceCommit, artifactSha256: artifact.sha256 }, null, 2));
        result.status = 'recorded-not-accepted';
      } else {
        const metadata = JSON.parse(await readFile(baselineJson, 'utf8'));
        assert.deepEqual(metadata.environment, environment, 'Baseline browser/OS differs; do not silently refresh it');
        assert.equal(metadata.contract, contract, 'Expected title/labels/regions changed; deliberate review required');
        const previous = await readFile(baselinePng);
        const comparisonPage = await context.newPage();
        for (let index = 0; index < regionPngs.length; index++) {
          const baselineRegion = await readFile(path.join(baselineDir, `${item.id}-region-${index}.png`));
          const comparison = await comparisonPage.evaluate(analyzeRaster, {
            png: regionPngs[index].toString('base64'), baselinePng: baselineRegion.toString('base64'),
          });
          result.regions[index].regression = comparison;
          assert.ok(comparison.dimensionsMatch && comparison.diffRatio <= REGION_MAX_DIFF,
            `Region ${index} visual regression exceeds ${REGION_MAX_DIFF}: ${JSON.stringify(comparison)}`);
        }
        result.regression = await comparisonPage.evaluate(analyzeRaster, {
          png: screenshot.toString('base64'), baselinePng: previous.toString('base64'),
        });
        await comparisonPage.close();
        result.baselineSourceCommit = metadata.sourceCommit;
        assert.ok(result.regression.dimensionsMatch && result.regression.diffRatio <= MAX_DIFF,
          `Visual regression exceeds ${MAX_DIFF}: ${JSON.stringify(result.regression)}`);
        result.status = 'passed';
      }
    } catch (error) {
      result.status = 'failed';
      result.errors.push(error.message);
      if (page && !page.isClosed()) {
        try { await page.screenshot({ path: path.join(outputDir, `${item.id}-failure.png`), animations: 'disabled' }); }
        catch { /* A crashed or navigated page may not permit a screenshot. */ }
      }
    } finally {
      await context.close();
    }
    if (result.consoleErrors.length || result.pageErrors.length || result.unexpectedRequests.length || result.errors.length) {
      if (result.status !== 'failed') result.errors.push('Browser side effect observed during final verification/cleanup');
      result.status = 'failed';
    }
    report.cases.push(result);
  }
  report.status = report.cases.some(item => item.status === 'failed') ? 'failed' : record ? 'recorded-not-accepted' : 'passed';
  if (selfTest) report.status = `selftest-${report.status}`;
  report.finishedAt = new Date().toISOString();
  await writeFile(path.join(outputDir, 'report.json'), JSON.stringify(report, null, 2));
  return report;
}

async function main() {
  const options = {};
  for (let index = 2; index < process.argv.length; index++) {
    const key = process.argv[index];
    if (key === '--record-baselines') options.record = true;
    else if (['--manifest', '--deps', '--baselines', '--output'].includes(key)) {
      assert.ok(process.argv[index + 1] && !process.argv[index + 1].startsWith('--'), `Missing value for ${key}`);
      options[key.slice(2)] = process.argv[++index];
    } else throw new Error(`Unknown option: ${key}`);
  }
  assert.ok(options.manifest && options.baselines && options.output,
    'Usage: node tests/browser/qa.mjs --manifest <json> --baselines <dir> --output <new-dir> [--deps <npm-root>] [--record-baselines]');
  const deps = path.resolve(options.deps ?? '.');
  const manifestFile = path.resolve(options.manifest);
  const manifest = validateManifest(JSON.parse(await readFile(manifestFile, 'utf8')));
  validateCoverage(manifest.cases);
  const { chromium, version } = playwrightFrom(deps);
  const assets = await loadCdnAssets(deps);
  const browser = await chromium.launch({ headless: true, args: ['--disable-background-networking'] });
  try {
    const report = await runArtifactSuite({ manifest, artifactRoot: path.dirname(manifestFile), browser,
      playwrightVersion: version, assets, baselineDir: path.resolve(options.baselines),
      outputDir: path.resolve(options.output), record: options.record });
    console.log(JSON.stringify({ status: report.status, sourceCommit: report.sourceCommit,
      passed: report.cases.filter(item => item.status === 'passed').length,
      failed: report.cases.filter(item => item.status === 'failed').map(item => ({ id: item.id, errors: item.errors })),
      report: path.resolve(options.output, 'report.json') }, null, 2));
    process.exitCode = report.status === 'passed' ? 0 : report.status === 'recorded-not-accepted' ? 2 : 1;
  } finally { await browser.close(); }
}

if (process.argv[1] && import.meta.url === pathToFileURL(path.resolve(process.argv[1])).href) {
  main().catch(error => { console.error(error.stack); process.exitCode = 1; });
}
