// ONE strict new numeric-boundary counterexample. NO browser or matrix replay.
// node extreme_heatmap.cjs COUNTEREXAMPLE_JSON EXISTING_TOOL_ROOT NEW_RESULT
const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
const crypto = require('node:crypto');
const [inputPath, toolRoot, resultPath] = process.argv.slice(2);
assert.ok(inputPath && toolRoot && resultPath);
assert.ok(!fs.existsSync(resultPath), 'Never overwrite prior evidence');
const input = JSON.parse(fs.readFileSync(inputPath, 'utf8'));
const g2Root = path.join(toolRoot, 'node_modules/@antv/g2');
const scaleRoot = path.join(toolRoot, 'node_modules/@antv/scale');
const g2Package = JSON.parse(fs.readFileSync(path.join(g2Root, 'package.json'), 'utf8'));
const scalePackage = JSON.parse(fs.readFileSync(path.join(scaleRoot, 'package.json'), 'utf8'));
assert.equal(g2Package.version, '5.4.8');
const {Linear} = require(path.join(g2Root, 'lib/scale/linear.js'));
const {createInterpolateValue} = require(path.join(scaleRoot, 'lib/index.js'));
// This is G2 runtime/scale.js inferOptionsQ's native default interpolator.
const nativeOptions = input.native.scale.color;
const scale = Linear({...nativeOptions, interpolate: createInterpolateValue});
const heats = input.native.data.map(row => row._heat);
const colors = heats.map(value => scale.map(value));
let ticks, tickError;
try {ticks = scale.getTicks();} catch (error) {tickError = String(error);}
const [low, high] = nativeOptions.domain;
const span = high - low;
const positions = heats.map(value => (value - low) / span);
const files = ['package.json', 'lib/scale/linear.js', 'lib/runtime/scale.js', 'dist/g2.min.js'].map(relative => ({library: '@antv/g2', relative, sha256: crypto.createHash('sha256').update(fs.readFileSync(path.join(g2Root, relative))).digest('hex')}));
for (const relative of ['package.json', 'lib/scales/continuous.js', 'lib/utils/normalize.js']) files.push({library: '@antv/scale', relative, sha256: crypto.createHash('sha256').update(fs.readFileSync(path.join(scaleRoot, relative))).digest('hex')});
const result = {source: input.source, finding: 'R38-18-F1', product_rows: heats, native_options: nativeOptions, g2: g2Package.version, scale: scalePackage.version, node: process.version, actual_scale_constructor: scale.constructor.name, consumer: 'Unmodified installed G2 CJS Linear factory with exact native domain/range and its documented-in-source default color interpolator.', span, positions, actual_colors: colors, expected_high_endpoint_rgb: input.expected_high_endpoint_rgb, high_endpoint_correct: colors[colors.length - 1] === input.expected_high_endpoint_rgb, ticks, tickError, files, strict_assertions: 1, browser_runs: 0, limits: 'Scale mapping only: no chart/canvas/legend paint/readiness/console/CDN health claim; not an attribution of role17 subnormal internal cause.'};
fs.writeFileSync(resultPath, JSON.stringify(result, (_key, value) => typeof value === 'number' && !Number.isFinite(value) ? {nonfinite: String(value)} : value, 2));
console.log(JSON.stringify({source: result.source, rows: heats.length, actual_colors: colors, high_endpoint_correct: result.high_endpoint_correct, strict_assertions: 1, browser_runs: 0}));
assert.equal(colors[colors.length - 1], input.expected_high_endpoint_rgb, 'The finite maximum must map to the high end of its literal native color range');
