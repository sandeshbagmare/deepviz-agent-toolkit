# Actual merged-main acceptance

Run once after an actual manager/root merge notification, never by polling.
The setup-only adapter confines `deepviz` to the immutable main source and
invokes the unchanged R26 verifier. The unchanged retained30 test file remains
`tests/r26_probes/role13/test_default_contract.py`; no oracle is copied/weakened.
All actual shipped test files are collected independently, unchanged.

Use `python -I -S verify_merged.py` with the R26 runner's original
`--source`, `--sha`, `--site-packages`, `--probe`, `--mode`, `--output` arguments
from an external empty CWD and a fresh output directory per distinct phase.
The original runner records exact HEAD, every tracked raw/GitLF byte, imported
model origin and runner/probe hashes before and after the real pytest process.
The adapter additionally proves its own unchanged bytes, source-only namespace
and absence of installed broader toolkit imports. No installs/persistent env
changes, test rewrites, xfails or repeat runs to obtain a preferred result.

`test_merged_mapping.py` adds only four bounded mixed-container roundtrip/error
and no-mutation controls, plus three strict canonical known728schema witnesses.
The latter remain actual failures until that separate schema slice lands; they
must not be misreported as new numeric #30 regressions or hidden as skips.
Published observations are real model JSON/errors/schema decisions, not chart
outputs. Browser/render/MCP/npm/scale are not implemented in this source slice.
