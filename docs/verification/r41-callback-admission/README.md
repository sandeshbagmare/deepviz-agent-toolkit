# Callback admission compatibility — R41

## Explicit manager decision

R04 explicitly accepted **canonical validated-data callback envelopes** for valid
bare JSON in `R41-four-live-refills-and-callback-source-release.md`. This is an
observable callback telemetry change, not byte-transparent compatibility.

Before this repair, a successful bare call exposed the original raw JSON as the
SDK's callback `input_str`, usually with `inputs=None`. Afterwards, the SDK sees
the same canonical envelope as an explicit `{"data": decoded_data}` call:
`inputs["data"]` is the decoded, validated dataset/reference; `input_str` is the
SDK's string representation of that envelope, not a promise of JSON formatting.
Whitespace, lexical number/escape spelling and exact original callback text are
not preserved. Explicit dictionary-form inputs retain their existing behavior.

**Migration cost:** a callback consumer depending on raw callback bytes or
`inputs is None` must migrate to the canonical `inputs["data"]` representation.
Consumers requiring byte-identical raw traces cannot treat this as transparent.
Do not restore raw unvalidated logging to work around the change. Callback
start/end/error order, counts, run IDs, tags, metadata, names and delegated
positional/keyword configuration are preserved, apart from this accepted input
representation change.

## Admission and public semantics

Only four lines are added to the existing public `ValidatedTool.run/arun`
overrides (the actual inner class spelling at the released e47 base): wrap a
string as `{"data": original_string}`, then reuse the existing dictionary
preflight. The original raw UTF-8 limit, strict decoded-equivalent duplicate-key
checks and depth admission run **before any SDK callback**, on original raw
input, not on a re-encoded approximation. The data is decoded once; no second
decode, context/global memo, file/Path cache, SDK hook, new backend or registry
policy is introduced. Existing finite-data serialization validation remains.
This does not establish a whole-process memory bound or performance guarantee.

Successful data/results, default normalization table/sample/max_points=200,
recommendation comparison goal, explicit goals/specs and caller input contents
remain unchanged. Bare encoded data/spec/goal objects are DATA, never unpacked
as tool kwargs. In particular bare rendering still lacks the required `spec`
and must fail, rather than silently gaining rendering defaults/authority.

The existing host-only `data_dir`, relative-path containment, handle lifetime
and original-source rereading remain authoritative. Canonical encoded file or
handle keys do not grant new filesystem authority. Unknown handles and unsafe
paths still reject. These later authorization/schema failures may legitimately
produce SDK start/error callbacks: the zero-callback guarantee concerns inline
admission, not every possible execution error.

## Evidence and scope

NEW permanent real-SDK controls:
`python/deepviz/tests/test_r41_callback_admission.py`. They exercise bare/dict
run, arun, invoke and ainvoke; original UTF-8/duplicate/depth rejection with no
callbacks/artifacts and same-tool recovery; exact raw limits; canonical trace
configuration; default sampling; no kwargs reinterpretation; one actual strict
decode before callback start (read-only call-entry profiling including executor
threads); file/handle authority; positional arguments; and actual synchronous
and asynchronous native PNG/SVG rendering.

The original role02 probes from2855f7 remain unedited. A separate identity
wrapper binds the actual committed repair and its six affected assertions;
original d65 identity code is preserved, never rewritten to pretend it proves
the new source. Actual executions/hashes/limitations are recorded in
`docs/coordination/reports/R41-16-callback-admission-implementation.md` and
`docs/coordination/evidence/R41-16/`. Author GREEN is not independent review,
CI, merge approval or release signoff. No normalizer/schema/cap/SDK/dependency
changes or full-suite/stdio/scale/10M replay belongs to this grant.
