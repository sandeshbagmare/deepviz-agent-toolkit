# R51 role09 — independent numeric-accounting TEST2

This directory contains only fresh bounded TEST2 probes for exact product
`96b819aee5b01ba88b5a609b587331a528aaa070` (parent `546c25ea75ee9d8a41b3832aa639664bc9a683b5`).
It is not a source change, producer approval, or replay of the R44 546 matrix.

The test cases independently cover huge mean/SUM cancellation at the unchanged
default 4300-digit limit, a mathematical `bit_length // 3 + 1` decimal-size
upper bound without converting the huge integer to text, ordinary/signed/finite
float/count outputs, natural 16-MiB retained-state rejection, zero and one-pass
behavior, input nonmutation, and strict unsupported-value errors. The budget
case uses a finite lazy stream and the unchanged public budget; it does not
monkeypatch caps or invoke private reducers.

The import guard proves the actual exact96 Git checkout and normalizer bytes.
Run from the exact96 checkout with the existing read-only venv, e.g.:

```powershell
& '<existing-venv>/Scripts/python.exe' -B -m pytest tests/r51_probes/role09/test_numeric_accounting_test2.py -q --disable-plugin-autoload --strict-markers --tb=short -p no:cacheprovider --junitxml=<unique-output>/tests.xml
```

Role11 TEST1 is a separate owner/result. Do not call this a combined numeric
approval or producer self-review; R04 compares both actual reports before any
role07 integration or PR/default decision.
