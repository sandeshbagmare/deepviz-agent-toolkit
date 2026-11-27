# R14 path/field collision integrity

Independent NEW tests for published source `5340bc69b7203ad7a9166543062482d819f9b705`.
The own branch's product/schema bytes were compared with that immutable target;
no normalizer, policy or old test is changed here.

From the repository root with prepared Python dev and npm dependencies:

```powershell
$env:PYTHONPATH = Join-Path (Get-Location) 'python/deepviz/src'
python -m pytest tests/r14_probes/role04/test_path_collision_integrity.py -q
python -m ruff check tests/r14_probes/role04
python -m mypy tests/r14_probes/role04
npm run build
node --test tests/r14_probes/role04/path-collision-integrity.test.mjs
python tests/r14_probes/role04/observe_path_grammar.py
node tests/r14_probes/role04/observe-path-grammar.mjs
```

POSIX: prefix Python commands with `PYTHONPATH="$PWD/python/deepviz/src"`.
No network, optional adapters, renderer, provider or install occurs in a test.
When reusing a build, verify its source identity first; do not load another
checkout's `dist`. The observations are **not normative tests** or passes.

## Independent invariant

- Same-row terminal path collisions must not choose last/first value silently.
  Current unescaped dotted naming cannot map both sources distinctly, so these
  cases require a concise public collision/ambiguity error. Both object orders,
  records/JSON/explicit selection and null contributions are tested.
- Noncolliding brackets, zero-prefixed strings, fullwidth dots, composed versus
  combining Unicode and Latin/Cyrillic lookalikes preserve **every** literal
  value/key and logical row count under explicit field mappings.
- Scalar columns and ordinary nested arrays have strict exact positives.
  Mixed scalar/nested column inference may preserve both columns or clearly
  reject ambiguity; this test does not invent a cross-language acceptance rule.
- Explicit `data_path` may intentionally select one branch; selecting that branch
  is not undisclosed data loss. Positive controls differentiate literal dotted
  sibling names, ASCII list indices and numeric-looking object keys.
- Guarded collision row1/41of60stops there; a normal60-row control exhausts past
  the32-row prefix. Iterator closure is not asserted (a separate lane owns it).
- Three negative controls prove the exact-value/count oracle rejects silently
  overwritten values, missing fields and wrong counts. No production mocks.

## Naming policy questions, not manufactured bugs

The observation scripts record non-ASCII decimal/zero-prefixed `data_path`
indices and bracket-like names. The contract promises dot-separated paths but
does not specify every index alphabet, escape or normalization. Report concrete
outputs/differences separately; a grammar difference alone is not an invariant
failure. Across-row literal and nested sources may deliberately share one output
field; both row identities/values are retained in a strict positive control.

Finite normalization tests do not certify renderer mappings, all input formats,
source-owner16's changes, process memory,10Mscale, current-MAIN or a final release.
