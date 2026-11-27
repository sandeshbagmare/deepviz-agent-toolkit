# Dedicated default-branch foundation QA

These NEW independent tests exercise only the Python contracts actually shipped
by default `main` at the recorded SHA. They do not import later rendering code,
install dependencies, change source or accept an unmerged PR as default.

The small wrapper must run with `python -I -S`: editable-install hooks are NOT
executed. It adds one explicit immutable source and one existing read-only
site-packages directory. Run from an external empty working directory. It
validates the loaded model path, exact HEAD, every tracked Git/raw byte and
unchanged own test/runner hashes before and after the actual pytest invocation.
The three deliberate wrong-provenance controls never edit source.

The first0ae2run's exact executed bytes are retained in
`docs/coordination/evidence/R26-13/executed-sources/*.py.txt`. Current files
subsequently received ONLY Ruff import ordering; import multisets and every
nonimport AST node are proven unchanged in `own-import-order.json`. Ruff was
rerun, **not** the unchanged default product tests. Runtime receipts name the
original executed hashes, not a false claim that the reordered bytes ran.
Use current files on the next actual merged-default notification, with fresh
source/probe hashes; never overwrite baseline receipts or archived sources.

```powershell
& '<existing venv>/Scripts/python.exe' -I -S verify_default.py `
  --source '<clean actual-default immutable snapshot>' --sha '<verified main SHA>' `
  --site-packages '<existing venv>/Lib/site-packages' `
  --probe '<OWN probes>/test_default_contract.py' --mode probe --output '<NEW output>'
```

Use `--mode shipped` once to execute the tests actually shipped at that snapshot.
A foundation containing no test files returns pytest **5**, zero tests; this is
not a passing suite. `--mode probe` runs only the NEW bounded public-contract
fixtures. Strict known numeric-type mismatches remain failures, not xfails or
weakened schema expectations. Generated schema/model outputs and observations
are source-specific and saved with JUnit/receipt; they are not chart artifacts.

Each phase requires a NEW output directory. Do not repeat unchanged-source runs
to stay busy or poll default/CI. After actual manager/root merge notification,
freeze the new default SHA, inspect its real shipped tests and run the affected
suite plus these retained smoke checks with new provenance and honest limits.
