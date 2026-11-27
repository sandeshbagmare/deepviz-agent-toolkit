"""ONE bounded R47 decision probe, not policy acceptance or old N11 replay."""
from __future__ import annotations

import datetime
import hashlib
import importlib
import json
from pathlib import Path
import sys
import types


def main() -> None:
    snapshot, output = map(Path, sys.argv[1:])
    source = snapshot / "python/deepviz/src/deepviz"
    expected = {
        "normalize.py": "34b88b4b959349593e9eac4e996c4996d311f9249daed1ee024606afd1af8dfc",
        "models.py": "890ecb0e29e1345364b2bf4840bdea7a542067003caf54d7b0855536ee2b6a76",
    }
    assert "deepviz" not in sys.modules
    for name, digest in expected.items():
        assert hashlib.sha256((source / name).read_bytes()).hexdigest() == digest
    # Read-only existing Pydantic; -I -S -B disables editable hooks/bytecode.
    deps = Path(sys.executable).parents[1] / "Lib/site-packages"
    assert deps.is_dir()
    sys.path.insert(0, str(deps))
    package = types.ModuleType("deepviz")
    package.__path__ = [str(source)]
    sys.modules["deepviz"] = package
    module = importlib.import_module("deepviz.normalize")
    models = importlib.import_module("deepviz.models")
    assert Path(module.__file__).resolve() == (source / "normalize.py").resolve()
    assert Path(models.__file__).resolve() == (source / "models.py").resolve()
    normalize = module.normalize
    spec = {"kind": "table", "aggregation": "none", "max_points": 10}
    key = "k" * 4097
    outer, inner = "a" * 2048, "b" * 2048
    assert len(key.encode()) == len((outer + "." + inner).encode()) == 4097
    selected_input = {key: [{"v": 7}]}
    before = json.dumps(selected_input, sort_keys=True)
    result = normalize(selected_input, {**spec, "data_path": key})
    assert result.records == [{"v": 7}]
    assert result.input_count == 1 and result.strategy == "none" and result.warnings == []
    assert json.dumps(selected_input, sort_keys=True) == before
    observations = [{"case": "4097-byte selector/root key discarded by explicit path", "admission": "ACCEPT", "input_count": result.input_count, "records": result.records, "unchanged_input": True}]
    for label, row in [
        ("4097-byte retained raw leaf key", {key: 7}),
        ("two 2048-byte segments, flattened name4097", {outer: {inner: 7}}),
    ]:
        try:
            normalize(iter([row]), spec)
        except ValueError as error:
            assert "field name" in str(error) and "4096" in str(error)
            observations.append({"case": label, "admission": "REJECT", "error": str(error)})
        else:
            raise AssertionError("Actual 4096-byte data-key guard unexpectedly absent")
    for name, digest in expected.items():
        assert hashlib.sha256((source / name).read_bytes()).hexdigest() == digest
    receipt = {"utc": datetime.datetime.now(datetime.timezone.utc).isoformat(), "product": "546c25ea75ee9d8a41b3832aa639664bc9a683b5", "probe_runs": 1, "bounded_decision_observations": observations, "module_origins": {"normalize": module.__file__, "models": models.__file__}, "exact_source_before_after": expected, "policy_acceptance": "NOT_CLEARED; four old64KiB-key RED not executed/waived", "scope": "Public normalizer module function, exact source; namespace bootstrap only avoids unrelated package SDK/render imports, not a full-package consumer. Read-only Pydantic; no production/constant/oracle/environment edits."}
    output.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"decision_probe": "PASS", "runs": 1, "observations": 3, "existing_64KiB_RED_replayed": 0, "accepted_4097_selector": True, "retained4097_raw_and_flattened_rejected": True}))


if __name__ == "__main__":
    main()
