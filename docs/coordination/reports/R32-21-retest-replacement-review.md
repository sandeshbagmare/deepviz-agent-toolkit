# R32-21 independent review/retest of NEW09 replacement

**What this change does:** The new verification recipe freezes candidate/runner
identity, invokes fixed explicit tools, validates structured totals, and checks
Python module origins inside the actual Pytest process. This review tests its four
original guard expectations on tiny SYNTHETIC fixtures, not the DeepViz product.

## Owner / immutable source / boundary

- SAME native reviewer21 `ses_de5678018ffezK8JGDUaSzvcWn`; OWN branch
  `agents/r10-21-recovery-git-bootstrap`, clean start **0305db8e6699d909e6e360a62dcf68274d6589ea**.
- FULL MAIN R22(97lines,09+21), R32(30lines),09handoff(84lines), currentAGENTS and
  ownnote read; prework report/note saved before source exploration and executions.
  Root10+6 admission is attributed, NOT a current or perpetual runtime census.
- **Exact reviewed/tested NEW code: b8736c514f1bad4d0d55cc513ec6de8af9e174a2.**
  Receipt **e549a489db289ba08cf82f97c95e6c15ec2eef2f** independently read by ONE
  `git ls-remote --heads origin refs/heads/agents/r10-09-helper-null-fix`, exit0,
  exactmatch. `git diff b873 e549 -- tests/r22_probes/role09/` empty/0.
- All5actual sources FULLread: PS108lines, Python154, Node9, README40, author tests306.
  Immutable Git blobs/hash manifest under evidence/R32-21/inputs/role09 and
  source-manifest.json. Author27tests were READ, **not rerun/borrowed as proof**.
- Allowed ONLY NEW report/evidenceR32-21/tests/r32_probes/role21/ownnote/OWNpublication.
  No09recipe/oracle/production/workflow/environment/API/install/spawn/poll changes.
  Original27testfile remains raw **b9c301946f9b30c6961e7549e3c66ed77be245681f020359d5920503c1200e0a**.
  New consumer uses its original fixture builder only; NONE of old27 tests run.

## Result: four original semantics independently verified at b873

**No new must-fix finding in this bounded scope.** Historical old-recipe findings
are not erased or retroactively made safe. The four NEW replacement behaviors now
have independent proof; R04/root decide adoption, no project/PR/CI approval here.

| Original expectation / exact subject lines | Actual independent reproduction / observed result |
|---|---|
| Source changed after preflight MUST reject and preserve pre/post evidence. PS73-84,101-105; Python21-39. | Original tiny fixture, npm stub appends to tracked render.ts on first build gate. Exit1, failure identity-changed, firststepEXECUTED/rest8NOT_RUN. Independent before/after digests differ; saved source-before equals before, source_after equals actual new bytes and dirty state. Same fixture HEAD, no false scoped PASS. `cases/c0`. |
| Untracked CWD import shadow MUST reject. Python25-30 / PS26. | Create untracked root deepviz/__init__.py; actual Python -c from that CWD imports THIS shadow despite candidate PYTHONPATH. NEWrecipe PLAN preflight exits1 before evidence allocation. No execution/plan acceptance. `cases/c1`. |
| Real all-skipped Pytest MUST NOT be scoped PASS. Python62-79,104-137 / PS87,93-96. | Actual four tiny Pytests collect4, Pytest exit0, JUnit4tests/4skips/0fail/0error. Wrapper rejects skipped totals, corestep exits1, final pack remainsNOT_RUN, receipt notPASS. Saved childPID/interpreter/modules and actual XML prove this was not fabricated skip metadata. `cases/c2`. |
| Duplicate PATH MUST allow ONE explicit expected tool dispatch positive. PS19-24,34-46,65,79. | Two real rogue npm.cmd/node.cmd locations on PATH proven by where.exe. All9fixed steps dispatch to exact explicit npm/node/interpreter paths, no rogue marker. Actual four tiny Pytests pass, same-process modules/rawhashes match requested synthetic source and independent session audit. Actual Node executes exact public-origin.mjs/--conditions=import on tiny import-only package and prints success. `cases/c3`. |

All subject references above are `tests/r22_probes/role09/{retest-helper-null.ps1,
recipe_guard.py,public-origin.mjs}` at b873. NEW assertions are in
`tests/r32_probes/role21/test_replacement_expectations.py:147-202`.
Fail-closed stopping at the FIRST bad gate is explicitly accepted; mutation/skip
negatives do NOT incorrectly require all9EXECUTED. No original semantic was weakened.

## Exact execution / honest failure history

Outer commands are preserved as argv/exits in *-run.json plus logs/XML; per-case
dispatch commands/stdout/exits are in cases/*/commands.jsonl and recipe receipts.
Fixture setup uses the unchanged original helper Git commands with exit0 assertions,
not a separately recorded syscall transcript. Final command:

```text
C:\Users\bagma\deepviz-agent-toolkit\.venv\Scripts\python.exe -m pytest tests/r32_probes/role21/test_replacement_expectations.py -q --tb=short -p no:cacheprovider --basetemp <OWN evidence/R32-21/raw/verified-temp> --junitxml <OWN evidence/R32-21/verified.xml>
```

Process-only `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1`; no shared environment modifications.
**Fresh final result: exit0 /4PASS /0FAIL /0ERROR /0SKIP /26.41s**,16:31:10-16:31:36UTC.
Probe SHA256 **57b0464286a0d277dc0f5ff9b747c4cd6337095cc776b9bb20a2504e14586120**.
Scoped Ruff0/mypy `--follow-imports=skip`0/1file; quality.json has actual commands.

Preserved OWN adapter/setup failures, never NEW09 findings or semantic RED:
1. first: exit1/4setupERROR0.64s, driver omitted parent raw directory; no recipe run.
   Created ONLY own missing parent; no test/source change.
2. second: exit1/3PASS1FAIL17.67s, duplicate fixture KeyError on copied case-sensitive
   envdict SystemRoot lookup BEFORE subject invocation. Use native os.environ lookup.
3. final(named earlier attempt): exit1/3PASS1FAIL33.01s; original dispatch/coreorigin
   positive already passed, extra actualNode proof saw own synthetic fallback.
   Minimal native diagnostic confirmed CMD splits raw --conditions=import into
   ARG1--conditions/ARG2import. Changed ONLY own predicate token; unchanged raw %*
   forwarded to actual Node. own-cmd-argument-diagnostic.json records real0/output.
4. verified: fresh4PASS26.41s after those owned fixes; no09/oracle source changes.

## Provenance and limits

- All5subject raw hashes equal b873 before/after every recorded outer run; original
  b9oracle hash unchanged. PS **19a2a0b6a719336a49a3011cef991a35be5df700f23e3a33133672f07dfab6b4**;
  Python **0b6832ec35bfd4247d2c460e7e398a9c7573095d59c7ee539cb2b8305dd3aebc**;
  Node **468c407d0cac321ec9c349dc5910000e8c430be867cf1073bd84ff282daadb92**.
- Four fresh fixture HEADs independently read back unchanged. Mutation case records
  actual dirty source; nonmutating cases retain tracked-byte identity. case-index.json
  links original test IDs, raw source-before/result, exact command outputs and digests.
- Tool-identity receipts capture actual Python/PowerShell/realNode plus explicit
  npm.cmd/node.cmd paths and before/after SHA256. Independent conftest session audit
  records childPID/executable/pytest path/count/exit and actual loaded module rawhashes;
  positive confirms a distinct childPID and match to guard's same-process origin receipt.
- The shared npm/node TEST commands deliberately emit **SYNTHETIC fabricated TAP36/282**
  to reach downstream guards without product execution. Build/typecheck/schema/pack
  stubs are NOT compilers/gates. Node public-entry RESOLUTION is real, not product JS
  evaluation/build. Inner4PASS and deliberate4SKIP are tiny fixtures, NOT689coretests.
- Zero product builds/tests/36or40oracle execution/npm282/core689/browser/render/MCP/
  DeepAgent/10M/envelope39/CI runs or installs. No fresh product/scale/release acceptance.
  Historical fifth finding about role11's production harness is OUTSIDE this retest.
- Source file origins/hashes do not attest Python bytecode/native dependencies or a
  trustworthy compiler. README27/38 explicitly limits baseline4 and trusted-tool lies;
  neither is presented as a newly fixed product guarantee or a new unsupported finding.
  No extra negative-case framework or padding was added beyond four requested cases.

**Verdict:** Accept the four requested guard behaviors for this exact NEW replacement
only; future product retests require their own authorized source, baseline totals,
actual dependencies/build/output and frozen-head gates. Do not use the old recipe.
**Next owner action:** R04/root record disposition/use NEW recipe for eligible05/R04
product retests without borrowing these synthetic totals. No release/PR/issue closure
or worker adoption is performed here. Own safe scoped publication/remote receipt next.

## Actual own publication, not product approval
C1 **8d12f266ae8d5baed3743d53807347a761817449** commit0/63OWNpaths;
2026-11-27T16:37:17.182234Z-16:37:26.686776Z nonforcepush0/exactownremoteSHA0.
Testedprobe57b046 unchanged;4PASS26.41s/Ruff0/mypy0 remain exactcode evidence.
Precommit62payloads232987B+stage-integrity, no rawruntime/Gitlinks/otherowners staged;
heuristicsecret0. TinySYNTHETICscope ONLY. Receipt-onlyC2next, no test/source changes.
