"""Setup-only adapter: retain R26 oracles and confine actual main imports."""

from __future__ import annotations

import argparse
import hashlib
import importlib
import importlib.util
import json
import os
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--site-packages", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args, _ = parser.parse_known_args()
    if not sys.flags.isolated or not sys.flags.no_site:
        raise RuntimeError("Run this adapter with python -I -S")
    sys.dont_write_bytecode = True
    os.environ["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] = "1"  # This child process only.
    actual = args.source.resolve() / "python/deepviz/src/deepviz"
    adapter = Path(__file__).resolve()
    before = hashlib.sha256(adapter.read_bytes()).hexdigest()
    sys.path[:0] = [str(actual.parent), str(args.site_packages.resolve())]
    namespace = importlib.import_module("deepviz")
    # Namespace packages may otherwise retain a broader installed sibling.
    namespace.__path__ = [str(actual)]
    runner = adapter.parents[2] / "r26_probes/role13/verify_default.py"
    spec = importlib.util.spec_from_file_location("r38_retained_runner", runner)
    if spec is None or spec.loader is None:
        raise RuntimeError("Cannot load the unchanged OWN R26 verification runner")
    retained = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = retained
    spec.loader.exec_module(retained)
    # Preserve the original verifier arguments and all behavior assertions.
    adapter_arguments = sys.argv[:]
    code = retained.main()
    after = hashlib.sha256(adapter.read_bytes()).hexdigest()
    if before != after or list(namespace.__path__) != [str(actual)]:
        raise RuntimeError("Adapter bytes or confined namespace changed")
    loaded = {
        name: str(Path(module.__file__).resolve())
        for name, module in sys.modules.items()
        if name.startswith("deepviz.") and getattr(module, "__file__", None)
    }
    if loaded != {"deepviz.models": str(actual / "models.py")}:
        raise RuntimeError("Unexpected broader product module imported")
    proof = {
        "argv": adapter_arguments,
        "adapter_sha256_before": before,
        "adapter_sha256_after": after,
        "retained_runner": str(runner),
        "retained_runner_sha256": hashlib.sha256(runner.read_bytes()).hexdigest(),
        "namespace_paths": list(namespace.__path__),
        "loaded_product_modules": loaded,
        "actual_pytest_exit": code,
        "scope": "Setup/provenance only; R26 runner and 30 assertions unchanged",
    }
    with (args.output / "setup-adapter.json").open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(proof, stream, indent=2)
        stream.write("\n")
    return code


if __name__ == "__main__":
    raise SystemExit(main())
