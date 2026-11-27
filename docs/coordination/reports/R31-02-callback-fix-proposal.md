# R31-02: minimal UNAPPLIED callback-admission proposal

## Actionable proposal and explicit compatibility limit

ONE patch: evidence/R31-02/bare-string-preflight.UNAPPLIED.patch. Against sealed e47f8701ad18bd3e3bc32a84bf4b2b3ea707ed23, add a two-line str-to-data-envelope branch before the EXISTING dictionary preflight in EACH public run/arun override: tools.py188-196. Four additions, zero deletions/import/helper/schema/SDK/resource changes. Do NOT apply it here; no production grant.

Reason: raw strings enter the same already-bounded canonical data path as explicit data dictionaries. Existing _inline_data validates ORIGINAL rawUTF8bytes, strict duplicate keys and depth BEFORE SDK callbacks; canonical decoded data is passed onward, so no second JSON decode, dump/reparse, global/context memo or resolved-Path cache. Later existing finite-data serialization checks remain unchanged. A tiny envelope is a shallow map, not a copied dataset; no renderer/registry capacity or new artifact resources are proposed. No RSS bound inferred.

IMPORTANT compatibility decision, NOT concealed: successful bare callbacks change from raw input_str/inputs=None to the SDK representation of canonical inputs.data. Counts/order and all args/kwargs delegation are intended unchanged, but exact callback payload text/shape is NOT preserved. R04 must explicitly accept that normalization contract before applying. If the request means exact raw callback payload preservation too, this four-line candidate DOES NOT satisfy that stricter requirement and MUST NOT be applied as a transparent fix. No approval or waiver is invented. Avoiding both a second parse and this public-envelope normalization while retaining raw trace shape would need additional adapter state/SDK hooks; none is authorized or proposed here.

Thus this is a concrete scope-safe candidate plus a surfaced compatibility decision, NOT a claim that every callback behavior is unchanged. Future strict recipe is evidence/R31-02/strict-acceptance-recipe.md. F1 remains OPEN until R04 decides/implements and actual new tools source is independently tested.

## Actual connected callchain inspected

- tools.py186-196 currently preflights ONLY dict/data; valid raw strings pass to superclass untouched. Installed LangChain-core1.8.5 base.py779-815 validates strings against FIRST schema field then returns the string;971-1005 supplies it positionally. base.py1074 starts sync callbacks BEFORE1092argument parsing; async1202 BEFORE1217. Patch ensures both public entrypoints canonicalize before those calls, not inside the later ToolSession function.
- BaseTool.invoke758-765 calls self.run; ainvoke768-775 calls self.arun. StructuredTool.ainvoke115-125 uses invoke executor when no coroutine, so sync override covers it. Explicit arun still needs its own branch. StructuredTool._run129-152 calls actual function; _arun174-185 uses coroutine or superclass executor fallback. No installed SDK method replaced or patched.
- Runtime argument metadata inspected WITHOUT calling a tool: RenderInput fields are data(required),spec(required). NormalizeInput keeps data first and default_factory=_profile_spec; RecommendInput keeps data first and default comparison goal. tools.py43-60/98-101/125-134 proves profile table/sample/max_points200 defaults. Dictionary schema path base.py835-888 supplies existing defaults; successful normalize/recommend results need future equivalence checks, not a source-only pass claim.
- tools.py22-40 retains original rawbyte1,000,000 and finite/canonical serialization limits; normalize.py73-86 strict object_pairs_hook rejects decoded-equivalent duplicate keys and translates recursion. Proposal does NOT use permissive json.loads, encode decoded data back into a raw string, or reinterpret encoded JSON keys as tool kwargs.
- tools.py77-95 remains sole reference boundary: sole file requires host data_dir, relative/non-drive/non-URL path and resolved containment; handle80-83 rereads existing stored original source. Unknown handles remain rejected. tools.py115-122 stores original bounded source, not resolved Path, max32 handles. Patch grants no new file authority, no raw scalar/path-string fallback and no resource/handle policy changes. File authorization errors remain later than inline admission; zero-callback claim is NOT extended to all _source failures.
- Bare render string still lacks required spec: do NOT silently turn encoded data/spec objects into a full call envelope or invent render defaults. Forward *args/**kwargs untouched. Existing schema/extra validation and callbacks remain delegated to SDK after successful inline admission.

## Exact original probes preserved

These are the TWO original Python files meant by this handoff, published in2855f7a4d051297e1d9e1246fd3051d35e2a11f0. Both remain unedited; current working hashes, GitLF hashes, published and current Git blobs match saved R22summary. CRLF-to-LF normalization is declared, not an assertion of raw/Git byte equality.

- tests/r22_probes/role02/source_identity.py: working SHA2566d0cc81fafe04dd4aa34e036d651168088051600152109e432ab838d6b304de6; GitLF SHA256ab43c9c2ccff2f4859b2d969d7091837615f717e2e1bca4eccf87cca6fcc9abc.
- tests/r22_probes/role02/test_p1_security.py: working SHA2564e325d644e0f8548d4c3bbe054121492bd0d6bf1da0b46d7ae24b0be2f0cc8db; GitLF SHA2563713f6d1886f21896715f992db615d5f820e5336bbeec49027d53c93caf23ac2.

Original six affected case assertions are unchanged: bare/dictionary run/arun invalid duplicate/rawbytes/depth callback-order+recovery, plus exactrawlimit two valid bare controls. No xfail/skip/oracle edits. Original identity helper is d65-pinned and cannot prove a future source: preserve it and use a NEW separate identity wrapper for actual repair. Future acceptance requires real NEW_PIN/tools Gitblob/import identity before running that affected six-case selection; no old8/2RED replay now. No genuinely uncovered counterexample justified another probe, so none created/executed.

## Exact source/static checks and actual outcomes

Owner SAME ses_de5678328ffeYCFXQhRPKd4a9h; own agents/r10-02-security-boundaries at7bb517e6e50454b5784e785d7ccbe585afd0780d when started, trackedclean. Three own old terminal publication receipts untracked and preserved, not staged. Full R31role02/R32root task packets/current canonical/RESUME/STATE/AGENTS/ownnote read; prework report/note saved BEFORE proposal construction.

Source consumer r25-02-mcp-p2-e47-ses_de5678328ffeYCFXQhRPKd4a9h is clean detached e47 before/after. P1d65/P2cd75 still sealed; no moving-main source assumption. Existing MAIN venv only, processlocal own-source PYTHONPATH and disabled bytecode. No install/environment mutation.

At16:24:02.225299UTC Python stdin static helper exit0: git rev-parse/sourceclean/blob equality; generated unified diff from immutable tools Git bytes; ast.parse candidate and structural comparison prove ONLY one added str-envelope branch per run/arun, all other AST identical; git apply --check PATCH exit0 in sealed consumer. --check is read-only: patch NOT applied, candidate NOT executed. Tools GitLF SHA25611273c5f5b0ff2eee16e09c6c727e560582a43fcae723bb315b6ef80d5a68495 and actual import resolve to e47. Patch SHA25677a69dfa0df1662ed95d6c033bcf5032ad2ede5bde85caf207095fbb4580688b. Any candidate-only in-memory hash is NOT an actual source commit or runtime result.

Actual installed SDK read-only hashes: base.py239c77d07a9283ced902fb161ca0fcdb5e532a9824caaa169ab014ac41c899d4; structured.pyf51689a1707c1ee31a173b8d8c9aaea33d994f4d95a79e6d51fe7369b2247142. Metadata introspection imports models only, no create_tools/run/arun/render/MCP call executed. Actual tests0/renders0/MCPrequests0/APIcalls0. No Ruff/mypy/product tests claimed for this unexecuted proposal; AST syntax/static equality and apply-check are their named limited checks only.

One long acceptance-document shell write was scanner-rejected BEFORE execution. Glob confirmed no partial recipe, bounded scoped writes succeeded. No result lost/false pass. Final hashes/source-clean/originals-unmodified are checked again before publication; static-proof.json records actual evidence.

## Limits and executable next action

This task grants only report/evidence/ownnote/OWNbranch writes: no production/fix, original probe, SDK, old oracle, package/schema/config/CI, GitHub API, install or spawn changes. No reuse of18 source ownership, no CI/head polling, no old8/2RED/SDK/stdio/capacity/fullsuite replay and no new broad audit. Mapping bff is the manager-provided milestone, not our new PR/default/merge acceptance. Earlier reports/author tests are NOT this proposal execution.

R04 next: explicitly disposition canonical successful trace payload versus exact-raw compatibility, then implement the four lines ONLY under its actual tools ownership after Mapping milestone. Commit/freeze real new tools SHA and hand it to independent02; preserve both original probes and execute strict affected recipe then. If raw trace preservation is mandatory, reject this candidate rather than claiming it satisfies that stronger requirement. No final signoff or source approval is granted here.
