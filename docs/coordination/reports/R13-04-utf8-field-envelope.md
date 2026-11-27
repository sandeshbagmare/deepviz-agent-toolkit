# R13-04 — recovered UTF-8 envelope publication and R04 disposition

**Status:** existing R10 publication/evidence reconciled; no command replay needed. Small own recovery/proposal publication pending actual execution. No source/policy/original-oracle edit, product fix, current-MAIN test pass or final acceptance claimed. 2026-11-27.

## Owner / reuse / authority

- SAME native ID `ses_de5678314ffeuDXtC7RfGsbD6V` confirmed by session_move. FULL MAIN R13common+04, own MAIN actual-ID note/R10report/finalreceipt, canonical/RESUME/STATE read before work. No new child/worktree/pin/reset, no service/provider/auth changes, no installs or spawning.
- Reused own `agents/r10-04-utf8-field-envelope` at `b2739ad38f544c1bfefe4ee2c687e24a476e05e3`, tested-code commit `2d9d2c15894ab9a5859d95060cd4fd3bba875061`, source checkpoint `3aa521a5d41e8f5cfcb21a5efc008bb3ff2cfcab`. R03immutable0c5and old96case matrices preserved.
- Allowed recovery writes: own note, NEWthisreport/`evidence/R13-04/`; no probe needed because no unfinished test gap found. Production normalizers remain16exclusive; global policy/original oracles untouched. R04aloneintegration/shared-push/issues/PRs. Rootadmission/ancestry was supplied by assignment; no worker runtime/headcount claim.

## First unfinished action resolved without duplicating commands

- Initial `git status --short --branch; git rev-parse HEAD; git log -3 --oneline`, working/indexdiff: own branchb2739ad, clean, bothdiffexit0. `git diff --exit-code 3aa521a5d41e8f5cfcb21a5efc008bb3ff2cfcab HEAD -- python packages schemas tests/test_n11_resource_policy.py` exit0. Existing source/oracles unchanged.
- Last foregroundR10receipt commit/push/readback already has savedexit0in MAIN finalreceipt. No prior background/in-flight command was recorded; none was restarted or polled. The first unfinished recovery action was fresh publication/result reconciliation, **not** rerunning completed104/105tests,96matrices/builds or10M.
- One bounded inlinePython collector via existing read-only `$PY=C:/Users/bagma/deepviz-agent-toolkit/.venv/Scripts/python.exe` exited0at2026-11-27T13:54:46.783785UTC. GCMstdout/stderr captured, token memory-only, no credential output/arguments/files or redirect following. AuthenticatedGET `/user`200expected`sandeshbagmare`; ownbranchrefGET200returned exactb2739ad=local; issue22GET200open. ZeroAPIwrites.
- Collector SHA-256 verified **nine source/module/fixture hashes and ten saved raw-artifact hashes, zero mismatches**; parsed savedJUnit and node logs rather than trusting a `succeeded` session label. Machine evidence: [`../evidence/R13-04/recovery-reconciliation.json`](../evidence/R13-04/recovery-reconciliation.json).

## Reconciled outcomes — saved checkpoint results, NOT new tests

| Saved check at3aa / tested-code2d9d | Saved exit / totals read back |
|---|---|
| NEW literal Python |0;104passed/0failed/0skipped, JUnit confirms104cases |
| NEW literal TypeScript |0;105passed/0failed/0skipped, node summary confirms105cases |
| NEW Python scoped Ruff/mypy; isolated TSbuild/noEmit |0each per saved source/checkpoint manifest; no rerun |
| Existing original N11 |**1;22passed/4failed/0skipped**, JUnit confirms26cases/0errors/exactfourfailure names below |
| Existing original N21 |0;23passed/0failed/0skipped, node summary confirms23cases |

Preserved controls describe **Python field4096bytes / cell65536bytes** versus **TS field+cell65536bytes**. Shared literals include4095/4096/4097names and65535/65536/65537cells/names across1-/2-/3-/4-byte units. Complete composite/`.0` index boundaries, exact value preservation/no truncation, invalidrow1/41of80pull stops, TSclosure and lazy512input→10output state/count/loss controls all remain byte-identical to their tested versions. Finite state rejection is not OS-memory or10M proof.

## Concrete handoff / proposal for the same four known policy failures

The existing failures are:

1. `test_exact_64kib_utf8_key_or_cell_is_preserved[key-ascii]`
2. `test_exact_64kib_utf8_key_or_cell_is_preserved[key-two-byte]`
3. `test_exact_64kib_utf8_key_or_cell_is_preserved[key-four-byte]`
4. `test_flattened_multibyte_key_at_64kib_is_preserved`

**One policy/oracle disposition, not four new independent tickets.** All expect64KiBname success against Python's documented4KiBguard; exact64KiBcell positives pass. The historical nested case rejects its oversized outer name before the final composite, so it cannot substitute for safe-component4096/4097composite tests.

Recommended minimal decision for **R04 only**, not applied here:

1. Approve explicit language-specific ingestion envelopes in the resource contract: Pythonnames≤4096, TSnames≤65536, bothcells≤65536UTF-8bytes; full dotted/indexed names count; reject rather than truncate. If common acceptance is required instead, route a separate owned change, do not silently widen Python.
2. Release a key-only correction of the N11positive boundary assertions: Python4096names preserved/4097rejected with literal ASCII/multibyte/composite/index coverage. Retain the old64KiBname cases as explicit rejection controls/evidence if useful; retain all65536/65537cell, record, retained-state, count/loss and reduction assertions. This author has not changed those existing oracles or policy.
3. Do **not** raise `_MAX_FIELD_BYTES` to make fourtests green. Existing Python schema-name retention has a stricter finite name envelope; widening needs separate state accounting and scale/resource evidence, not a one-line workaround. Keep16normalizer ownership intact.
4. After16handback and the actualR04decision, have genuine non-author reviewers/testers validate the exact candidate. Acceptance recipe: originalN11suite plus portable `tests/r10_probes/role04/test_utf8_field_envelope.py` and `utf8-field-envelope.test.mjs` built from that checkout, while preserving field/cell/record/state/count controls. Full candidate gates/CI/fourfinalreports remain independent requirements.

Real issue22is bounded-stream/scale context, still open in the fresh GET; this small finite test branch does not close it or create progress toward900by test-case multiplication. R04prioritizes real allocation/correctness fixes ahead of this oracle-only disposition.

## Publication / limits / next action

- Pending small scopedrecoverycommit: own actual-ID note, this report, sanitized R13reconciliationJSON only; explicit staging/whitespace/scope/credential checks before non-force own push and actual remote-SHA readback. No duplicate R10codecommit or newprobe for filler.
- Not rerun: completed tests/builds/lint/matrices/scales. Not claimed: currentMAIN execution, full-suite green, fixed fourREDs, finalCI, independent review/signoff, distribution/browser/visual/10M/RSS acceptance. Collector0is a reconciliation success, not a productpass.
- **Current action:** publish this verified recovery/disposition packet on the SAME ownbranch, then return actual receipt to root/R04forrollingtriage.
- **One executable next action (R04 after receipt):** `git show 2d9d2c15894ab9a5859d95060cd4fd3bba875061 -- tests/r10_probes/role04`, read this four-failure proposal, make the explicit policy/owner decision and arrange non-author candidate retests after16handback. This worker has no source/policy/oracle release.
