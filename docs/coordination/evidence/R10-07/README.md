# R10 role07 — Python distribution checkpoint evidence

**Issue:** [#24](https://github.com/sandeshbagmare/deepviz-agent-toolkit/issues/24), still open; this worker makes no issue/PR mutations. **Tested source:** `3aa521a5d41e8f5cfcb21a5efc008bb3ff2cfcab`, tree `cdb78b93e44b0e959702cfd13a88dc4e547fc1ef`. This is independent checkpoint testing, **not final-candidate signoff**.

| Acceptance | Actual result |
|---|---|
| Fresh exact-source sdist and wheel-from-sdist | Build exit0; no editable/shared source used by consumers |
| Strict Twine | Both archives passed, exit0 |
| Archive/RECORD/source identity | 26 assertions passed; wheel20members, sdist252files |
| Wheel base-only consumer | 27pass/0fail; one deliberate optional MCP transport skip |
| Separate direct sdist[mcp] consumer | 27pass/0fail/0skip; independent public dependency resolution, `pip check`0 |
| Actual console boundaries | Both installed `deepviz`/`deepviz-mcp` helps; Matplotlib PNG and native Vega SVG CLI2→2 |
| Actual installed stdio MCP | Initialize, seven tools, normalize→recommend→render, read PNG equal to inline PNG, reject unauthorized file, shut down |
| Installed typing | Both interpreters: valid API0; deliberate str→int assignment expected1 (not missing/untyped import) |
| Owned harness | 7pytestpass, Ruff0, mypy0/3scripts |

The first consumer run honestly stopped on **26pass/1own-harness-failure**: its new oracle assumed Vega emitted PNG, but the installed CLI correctly emitted SVG. The corrected strict MIME-aware oracle has positive SVG and invalid-PNG/non-SVG negatives. Original failure, executed harness, completed build/install and logs were preserved. Recovery reran only the corrected wheel probe into a **new** output and ran the still-unexecuted sdist consumer; no duplicate build or finished wheel installation.

## Actual output and rationale

All four images were opened in the image reader, not merely checked for existence. Both installed consumers produced identical image bytes per engine. Each shows exactly two bars with A=2 and B=5, zero-based quantitative axes, legible A/B category labels, `value`/`label` axes and the expected title. The local vl-convert raster preview displays the **actual native Vega SVG**, not a replacement renderer output. No clipping/extra marks observed in this small fixture. Native SVG, CLI manifests and raw images remain in the private local owned artifact root.

| Engine | Viewable fixture | Bytes | SHA256 |
|---|---|---:|---|
| Matplotlib wheel | [wheel-matplotlib.png](wheel-matplotlib.png) | 10,729 | `a6e73e95f4561291e5865bb16a309a6f56c002cc878cfa227cc6f6eb6ed7edc7` |
| Matplotlib sdist | [sdist-matplotlib.png](sdist-matplotlib.png) | 10,729 | `a6e73e95f4561291e5865bb16a309a6f56c002cc878cfa227cc6f6eb6ed7edc7` |
| Vega wheel SVG preview | [wheel-vega.png](wheel-vega.png) | 46,941 | `2bb6fd8b03ddc3e0c505138b8ec7075bf3dd82a78cdc8e5782ed9474355cf54a` |
| Vega sdist SVG preview | [sdist-vega.png](sdist-vega.png) | 46,941 | `2bb6fd8b03ddc3e0c505138b8ec7075bf3dd82a78cdc8e5782ed9474355cf54a` |

## Identity and replay

- Wheel: 52,845B, SHA256 `b99c5ec2836e9fed5dd794600ce228993e8c923a5972709a314f380449239f22`.
- Sdist: 666,560B, SHA256 `8e69e21cb2f39d4556be84bb2e4fafe078dc46f848631acc42917d88bf88c89f`.
- [distribution-result.json](distribution-result.json): exact installed origins/versions, imported backend/frontend/Twine identities, source/archive/resource hashes, all assertions, consumer command output and raw-evidence identities. Paths use portable placeholders; raw local values are preserved and hash-pinned.
- [commands.json](commands.json): exact completed child argv/cwd/exits/times, including initial failure and expected typing REDs.
- Replay: [owned harness instructions](../../../../tests/r10_probes/role07/README.md). The final portable runner includes the same separately exercised typing recipe and generic exact-snapshot archive checks; that wrapper was **not** used to repeat the already-completed build.

All installs used only declared public requirements/their dependency closure in three new worker-owned venvs. Python isolation was `-I`, system/user sitesfalse, inherited PYTHONPATH/private pip/uv config removed; public PyPI with no pip cache. This is not an offline/cache-only test. Shared main venv was a read-only launcher/lint/test tool, not consumer dependencies. No auth tokens, venvs, caches, datasets or dependency file trees are published.

**Limitations:** Windows/Python3.12.16 with one resolver snapshot, no minimum/maximum dependency or OS matrix. Deep Agent/provider/browser/CDN/scale/full project suite/current remoteCI/final-source validation not run here. The full suite would repeat packaging builds expressly prohibited in this recovery; no project-green claim. Author self-inspection is not an independent reviewer/tester approval; coordinator must arrange genuine review using existing authorized roles.
