# Portable MCP / Deep Agents lifecycle acceptance

This runs real MCP SDK stdio subprocesses and the actual Deep Agents graph with
deterministic local tool decisions. No provider/network-model call or host widget
integration is implied. The SDK process/stdout hooks observe, not replace, transport.

## Source mode (executed)

From the checkpoint checkout in PowerShell, select an existing Python containing
the project-declared runtime, MCP and agents extras. Do not install into shared envs.

```powershell
$py = 'C:\path\to\existing\Scripts\python.exe'
$env:PYTHONPATH = (Resolve-Path python/deepviz/src).Path
$env:PYTHONDONTWRITEBYTECODE = '1'
& $py tests/r10_probes/role10/test_portable_lifecycle.py `
  --mode source --expected-module-root $env:PYTHONPATH --output-dir C:\path\to\own\artifacts
& $py -m pytest tests/r10_probes/role10/test_portable_lifecycle.py -q -rs
```

The declared source checkpoint is `3aa521a5d41e8f5cfcb21a5efc008bb3ff2cfcab`.
The probe rejects production-source differences from that checkpoint. Future
source acceptance requires an explicitly updated checkpoint, not a silently
borrowed pass. Every execution uses a fresh task directory and records imported
module paths/hashes, versions, source identity and a summary.

## Clean installed mode (recipe, NOT executed here)

After an independently built/identified wheel is installed into a genuinely clean
consumer by the distribution owner, use **that consumer's** Python. First clear
`PYTHONPATH`; set an explicit expected wheel module root and compare the summary's
module hashes with the wheel receipt. No pytest is needed for the standalone run.

```powershell
Remove-Item Env:PYTHONPATH -ErrorAction SilentlyContinue
& C:\own\clean-consumer\Scripts\python.exe C:\probe-checkout\tests\r10_probes\role10\test_portable_lifecycle.py `
  --mode installed --expected-module-root C:\own\clean-consumer\Lib\site-packages `
  --output-dir C:\own\installed-artifacts
```

Installed mode rejects editable distributions, injected PYTHONPATH, checkout
imports, and modules outside the installed distribution's package directory. The
permanent editable-runtime negative control covers a real first-revision harness
mislabel; that failed attempt is excluded from installed-wheel claims.

## Strict oracles and limits

- Three actual stdio servers: discovery, five engines, 13 byte-equal resources,
  exact four source rows to three sums `7,11,-3`; SVG/PNG and manifest checks;
  JSON-RPC-only stdout and each process exits 0 after SDK stdin closure.
- Missing/evicted handles rejected; a copied handle retains source authority after
  original eviction; a new server has no prior handles/resources.
- Default file authority disabled; explicit configured-relative file positive,
  traversal/absolute/drive/URL/raw-string/output-dir negatives; deleted resources
  fail without killing the transport or altering an unrelated sentinel.
- A removed authorized source file leaves cached recommendation metadata, but
  rendering rechecks the file and fails. Handles are not immutable data snapshots.
- Seven local Deep Agent calls produce real artifacts and exact manifests; small
  tool-message payloads. Full resource downloads (e.g. Plotly library HTML) are not
  being described as tiny metadata envelopes.
- No filesystem-race sandbox, native browser/all-kind approval, scale benchmark,
  global resource-registry bound, live provider or final release claim. Windows
  symlink privilege checks are separate and remain explicit skips when unavailable.
