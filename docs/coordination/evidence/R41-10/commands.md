# Actual R41 role10 commands, exits and boundaries

Existing read-only tools: `C:/Users/bagma/deepviz-agent-toolkit/.venv/Scripts/python.exe`
and `C:/Users/bagma/deepviz-agent-toolkit/node_modules/typescript/bin/tsc`.
OWN branch root: `C:/Users/bagma/AppData/Local/Temp/opencode/r11-10-mcp-ses_de56782e3ffeI5D4lzsNVeLcDk`.
Set `A=C:/Users/bagma/AppData/Local/Temp/opencode/r41-10-546-artifacts-ses_de56782e3ffeI5D4lzsNVeLcDk`;
`S=C:/Users/bagma/AppData/Local/Temp/opencode/r41-10-546-source-ses_de56782e3ffeI5D4lzsNVeLcDk`.
Below `<python>` is that exact existing executable, not a new environment.

1. Native session_move returned actual SAME session `ses_de56782e3ffeI5D4lzsNVeLcDk`.
   `git rev-parse HEAD; git status --short --branch; git show -s --format="%H %s" 546c25ea75ee9d8a41b3832aa639664bc9a683b5`
   exit0: OWN682c7047 clean; product object exists. No current-main/CI inference.
2. `git -c core.autocrlf=false worktree add --detach <S> 546c25ea75ee9d8a41b3832aa639664bc9a683b5`
   exit0, new clean exact source. Original8GP files extracted by `git show acb11f862dd211a0563fd3dd824b8e5f5493ffaf:<path>`;
   original5prefixfiles by `git show 8dae3381e6caa0c99d6f032c2d2d318d5cf2a5ce:<path>`.
   Raw original/file hashes are in bindings.json; no original file edits.
3. OWN initial `python -m ruff check --no-cache tests/r41_probes/role10` exit0;
   `python -m mypy --cache-dir <A>/mypy-cache tests/r41_probes/role10` exit1:
   two annotation-only errors (`object.endswith`, yielded mixed-page object).
   Corrected ONLY own annotations BEFORE any product import/build/test; scoped
   recheck both0. `node --check` each twoMJS exit0.
4. With process-local `PYTHONPATH=C:/Users/bagma/deepviz-agent-toolkit/.venv/Lib/site-packages`
   and `PYTHONDONTWRITEBYTECODE=1`:
   `<python> -S tests/r41_probes/role10/driver.py setup --source <S> --output <A>/bound-run --compiler <existing-tsc>`
   exit0:24candidate+21baselineGitinputs/13unchangedoracles/38OWNemits. Actual
   compiler argv/output/exit0 for BOTH546 and exact6d0 are in bindings.json.
5. `<python> -S tests/r41_probes/role10/driver.py run --bindings <A>/bound-run/bindings.json`
   **exit1**. Exact threechildargv/exits/time/logSHA in actual-runs.json:
   - Python251:239PASS12FAIL0ERROR0SKIP/1.78sbody,2.5826698sprocess/exit1.
   - Node initial4FILE-level errors,0consumerassertions/exit1; unsupported Windows
     C: --import URL. Original stdout/stderr preserved, not product failures.
   - Four original fieldpolicy4FAIL0SKIP/exit1. No waiver/xfail/cap change.
6. Corrected ONLY launcher path binding to `Path.as_uri()`. Literal Py/MJS and
   preloadMJS remain byte-identical to first-code-hashes.json, verified by collector.
   `<python> -S tests/r41_probes/role10/driver.py node --bindings <A>/bound-run/bindings.json`
   **exit1**: corrected actualNode257/249PASS8FAIL0SKIP/558.8885msbody,
   0.7396314sprocess. node-resume-runs.json has actual file:// argv.
   SAMEbuiltJS, NO Python/policy/build replay; all234originalNodecases passed.
7. NEW separate three-row numeric positive lifetime cases (first mixed diagnostics
   failed BEFORE lifetime assertions, so were not claimed as ownership passes):
   `<python> -S tests/r41_probes/role10/driver.py ownership --bindings <A>/bound-run/bindings.json`
   **exit0:2PASS0SKIP/0.10s**. Real owned JSONL close/Winrename and borrowed
   StringIO-open/re-read assertions actually executed. All original diagnostic
   assertions/data left unchanged; source/module proof before+after saved.
8. Final OWN `python -m ruff check --no-cache tests/r41_probes/role10` **exit0**;
   `python -m mypy --cache-dir <A>/mypy-cache tests/r41_probes/role10` **exit0/fourPy**.
   Exact transcript final-quality.log; collector also AST-parses fourPyfiles.
9. `<python> -S tests/r41_probes/role10/summarize.py <A>/bound-run/bindings.json docs/coordination/evidence/R41-10`
   **exit0 = assembly ONLY**, overall **RED**. Rechecks all Git source/oracles,
   both builds/compiler hashes, clean546source, literal assertions unchanged,
   actual XML/TAPcases, four Node-before-consumer proofs and baseline-S proof.
   No product consumer/test/build replay. verification.json enumerates31copied
   evidence files/hashes and all observed cases/cohort classifications.
10. Explicit-path `git add -- <OWNsevenprobe files/report/evidence/role10/actualIDnote>`;
    all staged `git diff --cached --check` **exit0**. Existing Git newline filtering
    canonicalizes13evidencefiles ONLY. No config/source/oracle/result edit.
    `publication-byte-map.json` records original raw SHA256 and staged LF SHA256;
    actual reverse LF→CRLF comparison restores all13 original bytes exactly.
    Source/literal probe bytes unchanged. With this canonical mapping44files
    form the ONE meaningful code+evidence payload, not another test or inventory.

No installs, shared-environment/config/source/oracle mutations, GitHub API,
PR/issue/defaultbranch writes, nested agents, polling, scale/cost/provider/browser
or old COUNT/MCP/full-npm/matrix reruns. Native OWN Git commit/push/readback is
the only authorized pending publication action; actual receipt is in owned
status/role10.md and preserved artifact publication receipt, not a forecast.
