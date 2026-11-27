# R32-21 independent four-guard retest (SYNTHETIC, not DeepViz)

Exact subject b8736c514f1bad4d0d55cc513ec6de8af9e174a2 is frozen under
`docs/coordination/evidence/R32-21/inputs/role09/`; manifest checks raw hashes.
This NEW adapter reuses ONLY the immutable R16 original fixture builder (hash
b9c301946f9b30c6961e7549e3c66ed77be245681f020359d5920503c1200e0a).
It does not run/change that original27 file or the author's27 controls.

Four tests preserve original semantics: tracked mutation rejection+pre/post;
untracked CWD shadow rejection; actual4-skipped-Pytest rejection; duplicatePATH
explicit-tool positive. Mutation may stop after gate1; do not require all9EXECUTED.
Tiny npm/node TEST reports are explicitly fabricated SYNTHETIC TAP, NOT product
build/npm282/core689. The public-origin command uses actual Node on a tiny import-only
package; four tiny Python tests really run/pass/skip with child module-origin audit.

Use existing Python/Pytest/PowerShell/Node/Git only, no installs. Create parent
`docs/coordination/evidence/R32-21/raw/` BEFORE a fresh unique `--basetemp` (Pytest
itself creates its final directory). Run this one file with plugin autoload disabled
in that child process, `-q --tb=short -p no:cacheprovider`, unique basetemp and JUnit.
Full actual argv and source/probe hashes: `verified-run.json`; result4PASS26.41s.
Preserved first/second/final attempts are OWN setup/stub failures, NOT recipe bugs.

`raw/` contains ignored tiny Git fixtures; never stage nested repos. Compact exact
receipts/logs are committed under cases/ with -text so raw byte encodings survive.
No product/scale/envelope/browser/CI acceptance or default/PR changes. R04 decides
adoption; old historical unsafe recipe is not changed or retroactively approved.
