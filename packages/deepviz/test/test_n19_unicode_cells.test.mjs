import assert from 'node:assert/strict';
import test from 'node:test';

const entry = process.env.DEEPVIZ_N19_MODULE_URL ?? new URL('../dist/index.js', import.meta.url).href;
const {normalize} = await import(entry);
console.info(JSON.stringify({n19UnicodePublicEntry: entry}));

// Expected rows are literal Python-primary controls, not outputs of any parser or trim helper.
const matrices = [
  {
    name: 'all five Python-only whitespace codepoints have numeric empty and original-text controls',
    csv: [
      'id,value',
      'fs-number,"\u001c2.5\u001c"', 'fs-empty,"\u001c\u001c"', 'fs-text,"\u001cliteral\u001c"',
      'gs-number,"\u001d-3\u001d"', 'gs-empty,"\u001d\u001d"', 'gs-text,"\u001dliteral\u001d"',
      'rs-number,"\u001e4.25\u001e"', 'rs-empty,"\u001e\u001e"', 'rs-text,"\u001eliteral\u001e"',
      'us-number,"\u001f0.5\u001f"', 'us-empty,"\u001f\u001f"', 'us-text,"\u001fliteral\u001f"',
      'nel-number,"\u00856\u0085"', 'nel-empty,"\u0085\u0085"', 'nel-text,"\u0085literal\u0085"',
    ].join('\r\n') + '\r\n',
    expected: [
      {id: 'fs-number', value: 2.5}, {id: 'fs-empty', value: null}, {id: 'fs-text', value: '\u001cliteral\u001c'},
      {id: 'gs-number', value: -3}, {id: 'gs-empty', value: null}, {id: 'gs-text', value: '\u001dliteral\u001d'},
      {id: 'rs-number', value: 4.25}, {id: 'rs-empty', value: null}, {id: 'rs-text', value: '\u001eliteral\u001e'},
      {id: 'us-number', value: 0.5}, {id: 'us-empty', value: null}, {id: 'us-text', value: '\u001fliteral\u001f'},
      {id: 'nel-number', value: 6}, {id: 'nel-empty', value: null}, {id: 'nel-text', value: '\u0085literal\u0085'},
    ],
    mixed: true,
  },
  {
    name: 'only the document BOM is removed while complete cell FEFF identity survives',
    csv: '\uFEFF' + [
      'id,value',
      'front,"\uFEFF7"', 'back,"7\uFEFF"', 'both,"\uFEFF7\uFEFF"', 'only,"\uFEFF"',
      'spaced," \uFEFF7 "', 'spaced-only," \uFEFF "', 'middle,"a\uFEFFb"',
    ].join('\r\n') + '\r\n',
    expected: [
      {id: 'front', value: '\uFEFF7'}, {id: 'back', value: '7\uFEFF'}, {id: 'both', value: '\uFEFF7\uFEFF'},
      {id: 'only', value: '\uFEFF'}, {id: 'spaced', value: ' \uFEFF7 '}, {id: 'spaced-only', value: ' \uFEFF '},
      {id: 'middle', value: 'a\uFEFFb'},
    ],
    mixed: false,
  },
  {
    name: 'whitespace recognition never rewrites original nonnumeric and numeric-looking strings',
    csv: [
      'id,value',
      'leading-zero,"\u001c001\u001c"', 'plus-sign,"\u001d+2\u001d"', 'leading-dot,"\u001e.5\u001e"',
      'hex,"\u001f0x10\u001f"', 'negative-leading-zero,"\u0085-01\u0085"',
      'ascii-padding," \tunknown\t "', 'python-space-with-FEFF,"\u001c\uFEFF5\u001c"',
    ].join('\r\n') + '\r\n',
    expected: [
      {id: 'leading-zero', value: '\u001c001\u001c'}, {id: 'plus-sign', value: '\u001d+2\u001d'},
      {id: 'leading-dot', value: '\u001e.5\u001e'}, {id: 'hex', value: '\u001f0x10\u001f'},
      {id: 'negative-leading-zero', value: '\u0085-01\u0085'}, {id: 'ascii-padding', value: ' \tunknown\t '},
      {id: 'python-space-with-FEFF', value: '\u001c\uFEFF5\u001c'},
    ],
    mixed: false,
  },
  {
    name: 'integer zero canonicalization does not erase fractional or exponent negative zero',
    csv: [
      'id,integer,fraction,exponent',
      'raw,-0,-0.0,-0e0',
      'fs,"\u001c-0\u001c","\u001c-0.000\u001c","\u001c-0E+10\u001c"',
      'gs,"\u001d-0\u001d","\u001d-0.00\u001d","\u001d-0e-7\u001d"',
      'rs,"\u001e-0\u001e","\u001e-0.0\u001e","\u001e-0e0\u001e"',
      'us,"\u001f-0\u001f","\u001f-0.000\u001f","\u001f-0e-1\u001f"',
      'nel,"\u0085-0\u0085","\u0085-0.0\u0085","\u0085-0E+2\u0085"',
      'positive,0,0.0,0e-4',
    ].join('\r\n') + '\r\n',
    expected: [
      {id: 'raw', integer: 0, fraction: -0, exponent: -0},
      {id: 'fs', integer: 0, fraction: -0, exponent: -0},
      {id: 'gs', integer: 0, fraction: -0, exponent: -0},
      {id: 'rs', integer: 0, fraction: -0, exponent: -0},
      {id: 'us', integer: 0, fraction: -0, exponent: -0},
      {id: 'nel', integer: 0, fraction: -0, exponent: -0},
      {id: 'positive', integer: 0, fraction: 0, exponent: 0},
    ],
    mixed: false,
  },
];

for (const matrix of matrices) {
  for (const format of ['csv', 'tsv']) {
    test(`N19 Unicode cells: ${matrix.name} [${format}]`, () => {
      // These fixtures contain no payload commas; replace only their known carrier delimiters.
      const text = format === 'csv' ? matrix.csv : matrix.csv.replaceAll(',', '\t');
      const result = normalize(text, {kind: 'table', aggregation: 'none', format, max_points: 100});
      assert.deepEqual(result.records, matrix.expected);
      assert.equal(result.input_count, matrix.expected.length);
      assert.equal(result.strategy, 'none');
      if (matrix.mixed) {
        assert.equal(result.warnings.length, 1);
        assert.match(result.warnings[0], /mixed.*numeric.*value/i);
      } else {
        assert.deepEqual(result.warnings, []);
      }
    });
  }
}
