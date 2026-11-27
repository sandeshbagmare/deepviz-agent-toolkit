import assert from 'node:assert/strict';
import {mkdirSync, mkdtempSync, writeFileSync} from 'node:fs';
import {join} from 'node:path';
import test from 'node:test';
import {fileURLToPath, pathToFileURL} from 'node:url';

// The override verifies an explicitly archived immutable producer build, never dirty sibling source.
const entry = process.env.DEEPVIZ_N19_MODULE_URL ?? new URL('../dist/index.js', import.meta.url).href;
const {normalize, ValidationError} = await import(entry);
console.info(JSON.stringify({n19PublicEntry: entry}));
const identity = {kind: 'table', aggregation: 'none', max_points: 100};

function expectRows(text, format, expected, options = {}, warningPatterns = []) {
  const result = normalize(text, {...identity, format, ...options});
  assert.deepEqual(result.records, expected);
  assert.equal(result.input_count, expected.length);
  assert.equal(result.strategy, 'none');
  assert.equal(result.warnings.length, warningPatterns.length);
  for (const pattern of warningPatterns) assert.ok(result.warnings.some(warning => pattern.test(warning)));
}

function expectInvalid(text, format, message) {
  assert.throws(() => normalize(text, {...identity, format}), error => {
    assert.ok(error instanceof ValidationError, `expected public ValidationError, got ${error?.name}: ${error?.message}`);
    assert.match(error.message, message);
    return true;
  });
}

const quotedCases = [
  {
    name: 'CSV BOM CRLF and quoted embedded CRLF preserve complete logical records',
    formats: ['csv', 'auto'],
    text: '\uFEFFid,note,amount\r\n001,"north, \"\"quoted\"\"\r\nsouth\twing",2.5\r\n002,last,\r\n',
    expected: [{id: '001', note: 'north, "quoted"\r\nsouth\twing', amount: 2.5}, {id: '002', note: 'last', amount: null}],
  },
  {
    name: 'TSV BOM CRLF quoted tab and comma preserve exact field contents',
    formats: ['tsv', 'auto'],
    text: '\uFEFFid\tnote\tamount\r\n001\t"east\twest, \"\"quoted\"\"\r\nnext"\t3\r\n002\tfinal\t4\r\n',
    expected: [{id: '001', note: 'east\twest, "quoted"\r\nnext', amount: 3}, {id: '002', note: 'final', amount: 4}],
  },
  {
    name: 'CSV quoted multiline header is a literal field name',
    formats: ['csv'],
    text: '"first\nsecond",value\r\nalpha,7\r\n',
    expected: [{'first\nsecond': 'alpha', value: 7}],
  },
  {
    name: 'TSV comma inside quoted header is not a CSV separator',
    formats: ['tsv', 'auto'],
    text: '"geo,region"\tvalue\r\nwest\t8\r\n',
    expected: [{'geo,region': 'west', value: 8}],
  },
  {
    name: 'CSV trailing empty columns and quoted empty records remain logical rows',
    formats: ['csv', 'auto'],
    text: 'id,left,right\r\n1,"",\r\n2,,""\r\n3, , \r\n',
    expected: [{id: 1, left: null, right: null}, {id: 2, left: null, right: null}, {id: 3, left: null, right: null}],
  },
  {
    name: 'CSV quotes in header decode before mapping dotted literal keys',
    formats: ['csv'],
    text: '"metric.total","region\"\"label"\r\n2.5,west\r\n4,east\r\n',
    expected: [{'metric.total': 2.5, 'region"label': 'west'}, {'metric.total': 4, 'region"label': 'east'}],
  },
];

for (const fixture of quotedCases) {
  for (const format of fixture.formats) {
    test(`N19 ${fixture.name} [${format}]`, () => {
      expectRows(fixture.text, format, fixture.expected);
    });
  }
}

test('N19 quoted tabs inside CSV header require explicit delimiter, not data loss', () => {
  expectRows('"label\tcode",amount\r\n001,6\r\n', 'csv', [{'label\tcode': '001', amount: 6}]);
});

test('N19 TSV dotted column names are exact mappings, not nested input selectors', () => {
  expectRows('geo.lon\tgeo.lat\r\n-122.4\t37.8\r\n139.7\t35.7\r\n', 'tsv', [
    {'geo.lon': -122.4, 'geo.lat': 37.8}, {'geo.lon': 139.7, 'geo.lat': 35.7},
  ], {x: 'geo.lon', y: 'geo.lat'});
});

for (const [format, text] of [
  ['csv', 'id,label\r\n1,"closed"tail\r\n'],
  ['csv', 'id,label\r\n1,un"quoted\r\n'],
  ['tsv', 'id\tlabel\r\n1\t"closed"tail\r\n'],
  ['tsv', 'id\tlabel\r\n1\t"still\r\n2\topen'],
]) {
  test(`N19 malformed quoted text rejects clearly [${format}: ${JSON.stringify(text)}]`, () => {
    expectInvalid(text, format, /quote|delimited|CSV|TSV/i);
  });
}

for (const [format, text] of [
  ['csv', '"metric\"\"id","metric\"\"id"\r\n1,2\r\n'],
  ['tsv', '\uFEFF"metric\"\"id"\t"metric\"\"id"\r\n1\t2\r\n'],
]) {
  test(`N19 escaped quoted duplicate header names reject after decoding [${format}]`, () => {
    expectInvalid(text, format, /unique|duplicate|header/i);
  });
}

for (const [format, text] of [
  ['csv', 'id,label\r\n1,a,\r\n'],
  ['tsv', 'id\tlabel\r\n1\r\n'],
]) {
  test(`N19 missing or extra trailing fields cannot be silently repaired [${format}]`, () => {
    expectInvalid(text, format, /column|field|count/i);
  });
}

test('N19 a late malformed CSV row still rejects after the inference and retention prefixes', () => {
  const text = 'id,v\r\n' + '1,2\r\n'.repeat(45) + '99,3,unexpected\r\n';
  assert.throws(() => normalize(text, {...identity, format: 'csv', max_points: 10}), /column|field|count/i);
});

test('N19 numeric grammar preserves leading zeros signed nonnumbers and boolean strings', () => {
  expectRows('key,value\r\nleading,0012\r\nnegative,-01\r\nplus, +2 \r\nshort,.5\r\nhex,0x10\r\nboolean,true\r\nexp, -2.5e+2 \r\n', 'csv', [
    {key: 'leading', value: '0012'}, {key: 'negative', value: '-01'}, {key: 'plus', value: ' +2 '},
    {key: 'short', value: '.5'}, {key: 'hex', value: '0x10'}, {key: 'boolean', value: 'true'}, {key: 'exp', value: -250},
  ], {}, [/mixed.*numeric/i]);
});

test('N19 integer negative zero follows Python integer coercion without erasing floating negative zero', () => {
  expectRows('integer,fraction\r\n-0,-0.0\r\n', 'csv', [{integer: 0, fraction: -0}]);
});

test('N19 TSV whitespace nonfinite spellings and overflowing exponent preserve all positions', () => {
  const result = normalize('id\tvalue\r\n001\t -Infinity \r\n002\t+inf\r\n003\t1e999\r\n004\t  \r\n005\t0\r\n', {...identity, format: 'tsv'});
  assert.deepEqual(result.records, [
    {id: '001', value: null}, {id: '002', value: null}, {id: '003', value: null},
    {id: '004', value: null}, {id: '005', value: 0},
  ]);
  assert.equal(result.input_count, 5);
  assert.equal(result.strategy, 'none');
  assert.ok(result.warnings.some(warning => /non-finite/i.test(warning)));
  assert.doesNotThrow(() => JSON.stringify(result.records));
});

for (const [format, text] of [
  ['csv', 'id,value\r\n1,"\uFEFF7"\r\n2,"\uFEFF"\r\n3,"a\uFEFFb"\r\n'],
  ['tsv', 'id\tvalue\r\n1\t"\uFEFF7"\r\n2\t"\uFEFF"\r\n3\t"a\uFEFFb"\r\n'],
]) {
  test(`N19 a BOM inside a cell is content, not another document BOM [${format}]`, () => {
    expectRows(text, format, [{id: 1, value: '\uFEFF7'}, {id: 2, value: '\uFEFF'}, {id: 3, value: 'a\uFEFFb'}]);
  });
}

for (const [format, text] of [
  ['csv', 'id,value\r\n1,"\u00852.5\u0085"\r\n2,"\u001c"\r\n3,"\u0085literal\u0085"\r\n'],
  ['tsv', 'id\tvalue\r\n1\t"\u00852.5\u0085"\r\n2\t"\u001c"\r\n3\t"\u0085literal\u0085"\r\n'],
]) {
  test(`N19 Python-primary Unicode numeric whitespace does not trim preserved nonnumeric text [${format}]`, () => {
    expectRows(text, format, [{id: 1, value: 2.5}, {id: 2, value: null}, {id: 3, value: '\u0085literal\u0085'}], {}, [/mixed.*numeric/i]);
  });
}

for (const format of ['jsonl', 'auto']) {
  test(`N19 BOM CRLF JSONL preserves nested literal fields and blank-line record boundaries [${format}]`, () => {
    expectRows('\uFEFF{"id":"001","details":{"v":2},"literal.dot":"west"}\r\n\r\n{"id":"002","details":{"v":3},"literal.dot":"east"}\r\n', format, [
      {id: '001', 'details.v': 2, 'literal.dot': 'west'}, {id: '002', 'details.v': 3, 'literal.dot': 'east'},
    ]);
  });
}

const duplicateObjects = [
  ['nested-array', '[{"id":1,"samples":[{"lon":3},{"lon":4,"lon":9}]}]'],
  ['escaped-slash', String.raw`[{"id":1,"details":{"a/b":3,"a\u002fb":9}}]`],
  ['escaped-quote', String.raw`[{"id":1,"details":{"a\"b":3,"a\u0022b":9}}]`],
  ['empty-key', '[{"id":1,"details":{"":3,"":9}}]'],
  ['surrogate-pair', String.raw`[{"id":1,"details":{"😀":3,"\ud83d\ude00":9}}]`],
];
for (const [name, text] of duplicateObjects) {
  for (const format of ['json', 'auto']) {
    test(`N19 duplicate encoded keys reject before flattening [${name}/${format}]`, () => {
      expectInvalid(text, format, /duplicate.*key|repeated.*key/i);
    });
  }
}

test('N19 JSONL duplicate detection reaches a later CRLF record even when only ten rows are retained', () => {
  const text = '{"id":1,"v":2}\r\n'.repeat(45) + '{"id":99,"payload":{"k":3,"k":9}}\r\n';
  assert.throws(() => normalize(text, {...identity, format: 'jsonl', max_points: 10}), /duplicate.*key|repeated.*key/i);
});

test('N19 equal member names in distinct sibling objects and records are not duplicate source keys', () => {
  expectRows('[{"id":"a","left":{"x":1},"right":{"x":2}},{"id":"b","left":{"x":3},"right":{"x":4}}]', 'json', [
    {id: 'a', 'left.x': 1, 'right.x': 2}, {id: 'b', 'left.x': 3, 'right.x': 4},
  ]);
});

test('N19 canonically equivalent Unicode spellings remain distinct JSON member names', () => {
  expectRows(String.raw`[{"id":1,"\u00e9":3,"e\u0301":4}]`, 'json', [{id: 1, '\u00e9': 3, 'e\u0301': 4}]);
});

test('N19 distinct JSON literal and nested keys cannot collide after flattening', () => {
  expectInvalid('[{"id":1,"part.0":"literal","part":["nested"]}]', 'json', /collid|collision|duplicate/i);
});

test('N19 expression-looking values and spreadsheet formulas stay inert literal data', () => {
  assert.equal(Object.hasOwn(globalThis, '__deepvizN19TextExecuted'), false);
  expectRows('[{"id":1,"label":"globalThis.__deepvizN19TextExecuted=true"}]', 'json', [
    {id: 1, label: 'globalThis.__deepvizN19TextExecuted=true'},
  ]);
  expectRows('id,label\r\n1,=SUM(A1:A2)\r\n2,@SUM(1+2)\r\n', 'csv', [
    {id: 1, label: '=SUM(A1:A2)'}, {id: 2, label: '@SUM(1+2)'},
  ]);
  assert.equal(Object.hasOwn(globalThis, '__deepvizN19TextExecuted'), false);
});

test('N19 JavaScript source is rejected instead of executed or treated as an empty table', () => {
  assert.equal(Object.hasOwn(globalThis, '__deepvizN19TextExecuted'), false);
  expectInvalid('globalThis.__deepvizN19TextExecuted=true', 'auto', /content|format|JSON|delimited/i);
  assert.equal(Object.hasOwn(globalThis, '__deepvizN19TextExecuted'), false);
});

test('N19 quoted URL cells stay data while a source URL is neither fetched nor auto-opened', () => {
  const originalFetch = globalThis.fetch;
  let calls = 0;
  globalThis.fetch = () => { calls++; throw new Error('N19 forbids network access'); };
  try {
    expectRows('id,url\r\n1,https://example.invalid/n19.csv\r\n', 'csv', [{id: 1, url: 'https://example.invalid/n19.csv'}]);
    expectInvalid('https://example.invalid/n19.csv', 'auto', /content|format|JSON|delimited/i);
    assert.equal(calls, 0);
  } finally {
    globalThis.fetch = originalFetch;
  }
});

test('N19 a real host JSON path and file URL are not implicitly read as dataset contents', () => {
  const root = fileURLToPath(new URL('../../../artifacts/local/N19/ts-text-cf27e85/', import.meta.url));
  mkdirSync(root, {recursive: true});
  const path = join(mkdtempSync(join(root, 'host-input-')), 'must-not-open.json');
  writeFileSync(path, '[{"id":"host-only","value":91}]', 'utf8');
  expectInvalid(path, 'auto', /content|format|JSON|delimited/i);
  expectInvalid(pathToFileURL(path).href, 'auto', /content|format|JSON|delimited/i);
});

for (const [format, text] of [
  ['json', String.raw`[{"id":1,"payload":{"\u005f\u005fproto\u005f\u005f":{"n19Polluted":true}}}]`],
  ['csv', 'id,"constructor.prototype.n19Polluted"\r\n1,true\r\n'],
  ['tsv', 'id\t"__proto__.n19Polluted"\r\n1\ttrue\r\n'],
]) {
  test(`N19 decoded unsafe field names cannot pollute object prototypes [${format}]`, () => {
    assert.equal(Object.hasOwn(Object.prototype, 'n19Polluted'), false);
    expectInvalid(text, format, /unsafe|prototype|field/i);
    assert.equal(Object.hasOwn(Object.prototype, 'n19Polluted'), false);
  });
}

for (const format of ['arrow', 'parquet']) {
  test(`N19 opaque binary-looking text requires the documented external adapter [${format}]`, () => {
    expectInvalid('PAR1not-an-adapter', format, /unsupported|adapter|format/i);
  });
}
