import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {execFileSync} from 'node:child_process';
import {mkdtemp, readFile, writeFile} from 'node:fs/promises';
import {join, resolve} from 'node:path';
import {after, before, test} from 'node:test';
import {fileURLToPath, pathToFileURL} from 'node:url';

const source = resolve(process.env.R17_13_SOURCE);
const expected = '5e595a8f893955ce34a0e26553bb7bf257ea93ae';
const head = execFileSync('git', ['rev-parse', 'HEAD'], {cwd: source, encoding: 'utf8'}).trim();
assert.equal(head, expected, 'independent consumer must use the assigned immutable source');
assert.equal(execFileSync('git', ['diff', '--name-only'], {cwd: source, encoding: 'utf8'}), '');
const {render} = await import(pathToFileURL(join(source, 'packages/deepviz/dist/index.js')).href);
const playwright = await import(pathToFileURL(resolve(process.env.R17_13_PLAYWRIGHT)).href);
const output = await mkdtemp(join(resolve(process.env.R17_13_OUTPUT_PARENT), 'browser-'));
const hash = bytes => createHash('sha256').update(bytes).digest('hex');
const save = (name, value) => writeFile(join(output, name), JSON.stringify(value, null, 2), {flag: 'wx'});
const measured = [6249996250000, 6249997500000, 6249998750000, 6250000000000,
  6250001250000, 6250002500000, 6250003750000, 6250005000000];
const rows = values => values.map((value, index) => ({group: `g${index}`, value}));
const xy = values => values.map((value, index) => ({group: [-3, 0, 9][index], value, size: [1, 4, 9][index]}));
const cases = [
  {id: 'positive-240', kind: 'bar', rows: rows([2, 4, 8])},
  {id: 'negative-240', kind: 'bar', rows: rows([-2, -4, -8])},
  {id: 'scientific-signed-240', kind: 'bar', rows: rows([-9.999e120, 3e120, 9.999e120])},
  {id: 'fixed-negative-240', kind: 'bar', rows: rows([-0.000001, 1, 2])},
  {id: 'finite-upper-240', kind: 'bar', rows: rows([1e308, 1.5e308])},
  {id: 'aggregate-960', kind: 'bar', rows: rows(measured), width: 960, height: 540},
  {id: 'line-numeric-240', kind: 'line', rows: xy([1e12, 3e12, 5e12])},
  {id: 'area-numeric-240', kind: 'area', rows: xy([-2, 1, 4])},
  {id: 'scatter-240', kind: 'scatter', rows: xy([-9e30, 2e30, 9e30])},
  {id: 'bubble-240', kind: 'bubble', rows: xy([1, 2, 3]), size: 'size'},
  {id: 'histogram-240', kind: 'histogram', rows: rows([0, 1, 2, 3]), x: 'value'},
  {id: 'empty-240', kind: 'bar', rows: []},
  {id: 'single-240', kind: 'bar', rows: rows([9.999e120])},
  {id: 'single-pie-240', kind: 'pie', rows: rows([7]), carriers: ['html']},
  {id: 'unicode-one-series-240', kind: 'bar', rows: [
    {'群Ω': '甲<&', '値Ω': 1e12, series: '同<&'}, {'群Ω': '乙', '値Ω': 2e12, series: '同<&'},
  ], x: '群Ω', y: '値Ω', color: 'series', carriers: ['html']},
];
let browser;
before(async () => {
  browser = await playwright.chromium.launch({headless: true});
  const files = [];
  for (const relative of ['packages/deepviz/src/renderers.ts', 'packages/deepviz/src/render.ts',
    'packages/deepviz/dist/renderers.js', 'packages/deepviz/dist/render.js', 'packages/deepviz/dist/index.js']) {
    const bytes = await readFile(join(source, relative));
    const item = {path: relative, sha256: hash(bytes), bytes: bytes.length};
    if (relative.includes('/src/')) {
      assert.deepEqual(bytes, execFileSync('git', ['show', `${expected}:${relative}`], {cwd: source}));
      item.git_bytes_equal = true;
    }
    files.push(item);
  }
  await save('identity.json', {source_commit: head, source, imported_entry: join(source, 'packages/deepviz/dist/index.js'),
    files, node: process.version, browser: browser.version(), playwright_entry: process.env.R17_13_PLAYWRIGHT,
    executable: playwright.chromium.executablePath(), probe_sha256: hash(await readFile(fileURLToPath(import.meta.url))),
    test_author_is_not_source_author: true, no_installs_or_full_suite_or_scale: true});
  console.log(`R17_13_OUTPUT=${output}`);
});
after(async () => {await browser?.close();});

function measure(svg) {
  const outer = svg.getBoundingClientRect();
  const box = element => {
    const b = element.getBBox(), m = element.getScreenCTM();
    const corners = [[b.x, b.y], [b.x + b.width, b.y], [b.x, b.y + b.height], [b.x + b.width, b.y + b.height]]
      .map(([x, y]) => new DOMPoint(x, y).matrixTransform(m));
    return {left: Math.min(...corners.map(p => p.x)) - outer.x, top: Math.min(...corners.map(p => p.y)) - outer.y,
      right: Math.max(...corners.map(p => p.x)) - outer.x, bottom: Math.max(...corners.map(p => p.y)) - outer.y,
      width: b.width, height: b.height};
  };
  return {width: svg.viewBox.baseVal.width, height: svg.viewBox.baseVal.height,
    texts: [...svg.querySelectorAll('text')].map(text => ({...box(text),
      text: [...text.childNodes].filter(n => n.nodeType === 3).map(n => n.textContent).join(''),
      anchor: text.getAttribute('text-anchor'), font: getComputedStyle(text).fontFamily,
      font_size: parseFloat(getComputedStyle(text).fontSize), display: getComputedStyle(text).display,
      visibility: getComputedStyle(text).visibility})),
    axis: svg.querySelector('g > path')?.getAttribute('d') ?? null,
    marks: [...svg.querySelectorAll('.mark')].map(mark => ({...box(mark), tag: mark.tagName,
      attrs: Object.fromEntries([...mark.attributes].map(a => [a.name, a.value])),
      title: mark.querySelector('title')?.textContent ?? null})),
    executable_labels: svg.querySelectorAll('script, a, image, foreignObject').length};
}

function geometryChecks(fixture, observed, width, height) {
  assert.equal(observed.width, width);
  assert.equal(observed.height, height);
  assert.equal(observed.executable_labels, 0);
  if (fixture.kind === 'pie') {
    assert.equal(observed.axis, null);
    assert.equal(observed.marks.length, 1);
    assert.equal(observed.marks[0].tag, 'circle');
    assert.equal(+observed.marks[0].attrs.cx, width / 2);
    assert.equal(+observed.marks[0].attrs.cy, height / 2);
    assert.equal(+observed.marks[0].attrs.r, Math.min(width - 130, height - 130) / 2);
    return;
  }
  const values = fixture.kind === 'histogram' ? [2, 2] : fixture.rows.map(row => row[fixture.y ?? 'value']);
  const min = Math.min(0, ...values), max = Math.max(1, ...values);
  const numeric = observed.texts.filter(text => text.anchor === 'end');
  assert.deepEqual(numeric.map(t => t.text), [max.toPrecision(4), min.toPrecision(4)]);
  for (const t of numeric) {
    assert.ok(t.left >= 24 && t.right <= width, `numeric label clipped or on y title: ${JSON.stringify(t)}`);
    assert.ok(t.top >= 0 && t.bottom <= height && t.width > 0 && t.height > 0);
    assert.equal(t.font_size, 12);
    assert.equal(t.font, 'monospace');
    assert.ok(t.width / t.text.length <= 8, 'actual resolved font exceeds reserved ASCII glyph advance');
    assert.notEqual(t.display, 'none');
    assert.notEqual(t.visibility, 'hidden');
  }
  const axis = observed.axis.match(/^M([^,]+),65 V([^ ]+) H([^ ]+)$/);
  assert.ok(axis, 'explicit connected horizontal/vertical axis must exist');
  const left = +axis[1], bottom = +axis[2], right = +axis[3];
  assert.equal(bottom, height - 65);
  assert.equal(right, width - 65);
  assert.ok(left < right, 'legal minimum dimensions need positive horizontal plot width');
  if (fixture.kind === 'histogram') {
    assert.equal(observed.marks.length, 2);
    assert.equal(observed.marks.reduce((n, m) => n + Number(m.title.split(': ').at(-1)), 0), fixture.rows.length);
    return;
  }
  const near = (actual, expected) => assert.ok(Math.abs(actual - expected) <= 1e-6,
    `coordinate ${actual} differs from required ${expected}`);
  const y = value => height - 65 - (value - min) / (max - min) * (height - 130);
  if (fixture.kind === 'bar') {
    assert.equal(observed.marks.length, fixture.rows.length);
    observed.marks.forEach((m, i) => {
      const a = m.attrs;
      assert.equal(m.title, `${fixture.rows[i][fixture.x ?? 'group']}: ${values[i]}`);
      assert.ok(+a.width > 0 && +a.height > 0);
      near(+a.y, Math.min(y(0), y(values[i])));
      near(+a.height, Math.abs(y(values[i]) - y(0)));
      near(+a.x + +a.width / 2, left + (i + 0.5) / fixture.rows.length * (right - left));
    });
  } else {
    const x = fixture.rows.map(r => r.group), xmin = Math.min(...x), xmax = Math.max(...x);
    const expectedPoints = fixture.rows.map((_, i) => [left + (x[i] - xmin) / (xmax - xmin || 1) * (right - left), y(values[i])]);
    if (['line', 'area'].includes(fixture.kind)) {
      assert.equal(observed.marks.length, 1);
      const points = observed.marks[0].attrs.points.split(' ').map(p => p.split(',').map(Number));
      const actual = fixture.kind === 'area' ? points.slice(1, -1) : points;
      assert.equal(actual.length, expectedPoints.length);
      actual.forEach((p, i) => {near(p[0], expectedPoints[i][0]); near(p[1], expectedPoints[i][1]);});
      if (fixture.kind === 'area') {near(points[0][1], y(0)); near(points.at(-1)[1], y(0));}
    } else {
      assert.equal(observed.marks.length, fixture.rows.length);
      observed.marks.forEach((m, i) => {
        near(+m.attrs.cx, expectedPoints[i][0]); near(+m.attrs.cy, expectedPoints[i][1]);
        near(+m.attrs.r, fixture.kind === 'bubble' ? Math.sqrt(fixture.rows[i].size / 9) * 30 : 4);
      });
    }
  }
  for (const m of observed.marks) {
    assert.ok([m.left, m.top, m.right, m.bottom].every(Number.isFinite));
    assert.ok(m.left >= 0 && m.top >= 0 && m.right <= width && m.bottom <= height);
  }
}

for (const fixture of cases) for (const carrier of fixture.carriers ?? ['svg', 'html']) {
  test(`R17 independent ${fixture.id} ${carrier}`, {timeout: 10000}, async () => {
    const width = fixture.width ?? 240, height = fixture.height ?? 200;
    const spec = {kind: fixture.kind, title: 'R17 <literal> Ω', x: fixture.x ?? 'group', y: fixture.y ?? 'value',
      width, height, aggregation: 'none', max_points: 10, ...fixture.size ? {size: fixture.size} : {},
      ...fixture.color ? {color: fixture.color} : {}};
    const artifact = render(fixture.rows, spec, 'svg');
    assert.equal(artifact.input_count, fixture.rows.length);
    assert.equal(artifact.output_count, fixture.rows.length);
    assert.deepEqual(artifact.renderer_spec.normalized.records, fixture.rows);
    const content = carrier === 'svg' ? artifact.renderer_spec.spec.svg : artifact.html;
    const stem = `${fixture.id}-${carrier}`, path = join(output, `${stem}.${carrier}`);
    await writeFile(path, content, {flag: 'wx'});
    const context = await browser.newContext({viewport: {width: 1100, height: 800}, offline: true});
    try {
      const page = await context.newPage(), errors = [], requests = [];
      page.setDefaultTimeout(5000);
      page.on('console', m => {if (m.type() === 'error') errors.push(m.text());});
      page.on('pageerror', e => errors.push(String(e)));
      page.on('requestfailed', r => errors.push(`request failed: ${r.url()}`));
      page.on('request', r => {if (/^https?:/.test(r.url())) requests.push(r.url());});
      await page.goto(pathToFileURL(path).href, {waitUntil: 'load'});
      if (carrier === 'html') await page.waitForFunction(() => globalThis.deepvizReady === true);
      await page.evaluate(() => document.fonts.ready);
      const svg = page.locator(carrier === 'html' ? '#chart-0 > svg' : ':root');
      const observed = await svg.evaluate(measure);
      const runtime = carrier === 'html' ? await page.evaluate(() => globalThis.deepvizErrors) : [];
      const png = await svg.screenshot();
      await writeFile(join(output, `${stem}.png`), png, {flag: 'wx'});
      await save(`${stem}.json`, {fixture: fixture.id, carrier, width, height, observed, errors, runtime, requests,
        source_commit: head, normalized_records: artifact.renderer_spec.normalized.records,
        input_sha256: hash(content), png_sha256: hash(png)});
      assert.deepEqual([errors, runtime, requests], [[], [], []]);
      geometryChecks(fixture, observed, width, height);
      assert.equal(await svg.evaluate(element => element.querySelector('title')?.textContent), spec.title);
      const field = fixture.y ?? 'value';
      if (fixture.kind !== 'pie' && fixture.kind !== 'histogram') assert.ok(observed.texts.some(t => t.text === field));
    } finally {await context.close();}
  });
}

test('R17 finite-format sweep keeps positive minimum-width plot and rejects illegal width', () => {
  let longest = '';
  for (let exponent = -323; exponent <= 308; exponent++) for (const mantissa of [-9.999, -1, 1, 9.999]) {
    const value = mantissa * 10 ** exponent;
    if (Number.isFinite(value) && value.toPrecision(4).length > longest.length) longest = value.toPrecision(4);
  }
  assert.ok(longest.length <= 12);
  assert.ok(240 - Math.max(65, 32 + 8 * longest.length) - 65 > 0);
  assert.throws(() => render(rows([1]), {width: 239}, 'svg'), /width must be an integer/);
});
