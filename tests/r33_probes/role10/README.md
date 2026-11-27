# Deferred first-native consumer preparation

`native_consumer.py` is preserved R33 partial acceptance code. **Product execution
NOT RUN**; it is not validated against a future native release. Direct R34
steering superseded further work. Initial own AST passed; Ruff/type findings were
limited to own subprocess spelling/type narrowing, with corrected static results
recorded in the report. No product tests, outputs, source imports or approvals.

Only after R04 supplies the actual new native head, confirms the API/CLI and
raw-string-path policy, and provides its module hash manifest:

```text
python tests/r33_probes/role10/native_consumer.py \
  --source-root <actual-native-checkout> --expected-commit <full-actual-native-SHA> \
  --hash-manifest <R04-JSON> --dependency-root <existing-read-only-site-packages> \
  --work-root <own-approved-temp-parent>
```

These are **consumer-harness flags**, not proposed product flags. Manifest shape:
`{"commit":"<actualSHA>","files":{"python/deepviz/src/deepviz/<each.py>":"<Git-blob-SHA256>"}}`;
complete package Python files required, no guessed hashes or current old target.
The actual referenced product CLI is `python -S -m deepviz.cli render INPUT
--spec SPEC --engine matplotlib --output-dir OUTPUT`: success JSON/exit0, invalid
spec empty stdout/concise existing stderr/exit2. No invented JSON error interface.

Open R04 decisions: preserve this CLI shape without absent tools dependencies in
the new slice; confirm public `deepviz.render.render`/Artifact result; define
whether a bare existing-path string at the direct API is rejected or is explicitly
host-authorized compatibility. This consumer NEVER converts a model string to a
Path/command, and makes no claim about that undecided API surface. Its strict
model `data_path` negative uses only an OWN outside sentinel. Separate06 owns
actual visual-semantic inspection; header/XML/manifest checks are not paint proof.
