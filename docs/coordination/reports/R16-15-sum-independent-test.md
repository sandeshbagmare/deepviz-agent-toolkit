# R16-15 independent SUM candidate test — scoped PASS

Owner/session `ses_de56780c8ffe7LgwvwdfR5qFQD`, non-author tester,2026-11-27.
Full MAIN task `R16-sum-independent-and-boundary-followups.md` common+15 and
current canonical/own-note/R10/R13/source-handback report read before work.
Own evidence branch `agents/r10-15-owned-input-cleanup`, parent8a10108; source is
**a separate clean detached worktree at ec9f669eff28cd5351da142765b7755e3b2f484f**.
Do not mistake the older production bytes on this evidence branch for tested source.

## Independent execution, not borrowed author evidence

Created unique isolated source consumer with `git worktree add --detach <new-path>
ec9f669eff28cd5351da142765b7755e3b2f484f`, exit0/initially clean. Actual import
resolved that worktree.23source/config/permanent-test paths were byte-identical
to raw committed Git blobs before and after all checks. Test SHA256:

- Python `cbb18b1ab0107ab4cfd4dfff1515b6c6afc5f4495b4a9b56be090dfb2bce610f`
- TS `72c909dfe855c107e6205683b7a3c36de269c56a39f4e999c4ad055118a93fcc`

Existing project Python/toolchain read-only, no installs, own PYTHONPATH,
bytecode disabled/pytest plugin autoload disabled. Windows11/Python3.12.16,
Node26.13.1/TypeScript7.0.2. From clean source worktree, actually ran:

```text
python -m pytest python/deepviz/tests/test_r07_finite_overflow.py -q --strict-markers -rs -p no:cacheprovider --basetemp <own-artifacts>/pytest-author23 --junitxml <own-artifacts>/independent-author23-python.xml
tsc -p packages/deepviz/tsconfig.json
node --test packages/deepviz/test/test_r07_finite_overflow.test.mjs
```

**Python23pass0fail0skip2.37s/exit0; TS23pass0fail0skip889.057ms/exit0.**
Fresh compile exit0: dist absent beforehand,19actual compiled files hashed,
index/normalize source maps identify actual relative source inputs, bridge hashes
the imported compiled modules. Build/source hashes unchanged after testing. This
is an independent run of unchanged tests, not reuse of author's23/23/269npm pass.

## NEW exact-value controls

Own NEW `tests/r16_probes/role15/` only.17fixtures, each five public modes:
Python records/guarded one-pass iterator, TS records/guarded sync/async streams.
Literal binary64 inputs -> exact `Fraction.from_float` rational sum -> Python
float rounding; compare exact big-endian bits. This does not copy the candidate
fallback. Explicit output memberships avoid copying group/eviction algorithms.

Covers signed promotion/residual, pre-promotion compensation, odd-mantissa tie
and values infinitesimally above/below via minimum subnormal, negative tie,
subnormal cancellation, maximum reconstruction, late promotion after37zero rows,
interleaved independent groups/empty group, state promoted before/after other-
bucket eviction and reserved-label collision. Genuine positive/negative final
overflow separately requires warnednull. Ordinary compensated positive control
does **not** imply universally correctly-rounded fastpath arithmetic.

Inputs transported to JS must preserve exact bits. Outputs require expected bits,
group values/counts, full source consumption, strategy, warning class/count and
complete within-language array/stream output equality; all finite-or-null JSON.
Max42inputrows/10outputrows.85mode executions are **17tests**, not85tests/issues.

Publication-version actual command from evidence worktree with source environment:

```text
python -m pytest tests/r16_probes/role15/test_sum_independent.py -q --strict-markers -rs --tb=short -p no:cacheprovider -o junit_family=legacy --basetemp=artifacts/r16-15/pytest-published --junitxml=artifacts/r16-15/new-independent-sum-published.xml
python -m ruff check tests/r16_probes/role15
python -m mypy tests/r16_probes/role15 --cache-dir artifacts/r16-15/mypy-cache
node --check tests/r16_probes/role15/sum_bridge.mjs
```

**17pass0fail0errors0skip2.71s/exit0**, Ruff0/mypy0(2files)/Node syntax0.
Portable setup in new README. No production/existing-oracle edits or copied dirty
candidate; source consumer remains tracked clean. Unchanged23suites run once.

## Honest harness corrections and evidence

Initial new run17failed2.11s because OWN adapter incorrectly called model_dump
on NormalizedData dataclass; corrected only own adapter to asdict/types/imports.
Own initial Ruff1/mypy3errors corrected, not product defects. Corrected17pass1.63s
then new tests strengthened exact warning/output parity for publication run above.
First metadata reader exit1 assumed UTF8 for PowerShell UTF16-BOM log; corrected
only reader, retained initial error capture. No source or expected-number changes.

Final readonly source/build/test/JSON/XML readback exit0. Raw logs/XML, node output
and detailed metadata remain local untracked. Compact sanitized evidence:
`docs/coordination/evidence/R16-15/{summary,source-build-identity}.json`, including
all source/config/test/compiled hashes and actual17expected fixture results.
Actual own commit/nonforce push/remote-SHA receipt is saved in MAIN after execution.

## Decision and boundaries

**No discrepancy found in this scoped SUM value acceptance.** R04 owns integration,
issue/PR disposition and all final gates; normalizer author16's previous handback
remains effective.02state-security/11performance/20artifact lanes are separate.
No new mean/fullsuite/scale/performance/gallery/package-consumer repetition.
Prior64ownership tests immutable/not replayed; prior genuine cleanup RED unresolved
and not implied fixed by this SUM pass. No new tickets, final head signoff, whole-
project green/CI/900 or measured-memory claim. Future changed candidate must rerun
affected tests independently with exact source/build provenance.
