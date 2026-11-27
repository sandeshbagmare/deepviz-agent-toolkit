# R13-15 independent reducer/error ownership — strict RED

Owner `ses_de56780c8ffe7LgwvwdfR5qFQD`, SAME-ID recovery/refill,2026-11-27.
Reused own branch `agents/r10-15-owned-input-cleanup`, parent/published60599dd;
requested source checkpoint `5340bc69b7203ad7a9166543062482d819f9b705`.

## Scope / source identity

Entire `python/deepviz/src` equals exact5340 (`git diff --exit-code ... HEAD --
python/deepviz/src` exit0). Branch wholecommit is60599dd, **not falsely called5340**.
Actual own imported normalize SHA256:
`0473bce148e96d0095a46b95577ec43bf5bc70050cfed1de37e8ab24c377bb83`.
Do not copy16's dirtySUMsource; future committed candidates need independent rerun.
Normalizers16-exclusive; no production/existing-oracle changes/installs/spawns.

Completed R10 cleanup13RED/30pass43case handoff remains untouched, not rerun.
These NEW21cases target valid-prefix reducer state budget, carrier I/O and early
stop ownership. One existing cleanup work item, not4/21newbugtickets. Root point
of contact; R04 owns issue/PR/integration; own small scoped publication only.

## Exact execution / outcomes

Existing project venv read-only, ownPYTHONPATH, bytecodeoff/pytestpluginsoff.
Python3.12.16/pytest9.2.0/pyarrow26.0.1/Windows11. Portable recipe in new README.
Actual final command (existing Python interpreter):

```text
python -m pytest tests/r13_probes/role15/test_reducer_source_ownership.py -q --strict-markers -rs --tb=short -o junit_family=legacy --basetemp=artifacts/r13-15/pytest-published --junitxml=artifacts/r13-15/reducer-ownership-published.xml
python -m ruff check tests/r13_probes/role15
python -m mypy tests/r13_probes/role15 --cache-dir artifacts/r13-15/mypy-cache
```

**pytest exit1:17pass/4fail/0skip5.73s. Ruff0, mypy0(1file).**
Initial8fail/13pass6.07s included4OWN samplingfixture errors(max_points1<10), not
productbugs; fixedonlynewfixture to legal10/expectedlen10. Followup4fail/17pass4.63s
preceded narrowtyping correction; allrawinitial/followup/published logs preserved.
Initial ownmypy3errors then2overrideerrors were not promoted to pass. Installed
typeshed's own TextIO definitions require precise overrideignore against byteIOBase;
same narrow typeignore applied only to new textfaultadapter, no broad suppression.

## Actual failure and positive discrimination

All4REDs are CSV/JSONL/ArrowIPCstream/Parquet ownedPath handles on **real public
16MiB retained-state guard**, no cap patch/private reducer invocation:
retained traceback frames `normalize→add→_check_retained_bytes`, **prefix32,
input_count256**, `.closed=[false]`, rename `PermissionError/errno13/WinError32`.
Actual rename succeeds after test-ownedcleanup in everycase. No bad fieldnames,
malformed cells, parser/inference failure or SUMnumeric mutation causes this RED.

17GREENcontrols:4onegroupreducerfullconsumption(270→1,count270,ownedclose),
4borrowedCSV/JSONLguard/fullconsumption(stayopen),1borrowedArrowreaderfuturebatch
readableafterguard,4deterministicEIOafter48validrows(ownedclose/borrowedstayopen),
4samplingmax_points10controls consume64rowsretain10(ownedclose/borrowedstayopen).
EIO injection wraps real files; this is deterministicfaultinjection, not evidence
of physical diskfailure. It demonstrates carrier-side unwinding works while outer
reducer-side failure leaves suspended source contexts open.

Finite fixtures270rows/legal65,520ASCIIbytegroupcells, explicitcount/x/y and512group
limit. Largest actual fixture17,695,768B, CSV17,691,214B/JSONL17,694,450B,
Parquetunique836,514B. Each file<18MiB, streamed writes/32rowcolumnarbatches.
Repeatedonegroup controls matchvolume but tinyretainedstate. This is a payload-bound
test, **not measured processRSS**. No OOM/unboundedfixture/resourcepolicymutation.

## Proposal, publication and limitations

Extend F1acceptance through reducer/reservoir operation failure, not just validation:
guaranteed owned-source unwind across inference/plan/consume/finalize, without
transferring callertext/Arrowreaderownership. Preserve all17positives including
remaining borrowedArrowbatch. R04/16 implements only after sourcehandback; nofixhere.

Compact evidence in `docs/coordination/evidence/R13-15/summary.json`; rawlogs/XML,
synthetic fixtures and identityreadback remain localuntrackedartifacts. Hash/JUnit
readback independently validates rowcounts/stage/renamebefore-after. Actual commit,
nonforcepush and remoteSHA receipt is MAIN-only after commandexecution; no preclaim.

No final frozen-source approval/fullbuild/browser/MCP/DeepAgent/scale/900claim.
Actual Windows locks checked; otherOS handle oracle portable but not executed here.
Optional pyarrow zero-skips here; absence on another machine is a skip, not pass.
No issue/PR mutations, no fake parameter→ticket decomposition or borrowedsignoff.

**Next:** R04/16 takes the NEW21strict tests plus previous immutable ownership tests,
repairs guaranteed-owned cleanup without closingborrowedinputs, and requests fresh
independent exactcandidate testing/review/CI. Do not blindly integrate RED as release.
