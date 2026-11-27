"""Guard selected callback probes against exact product and installed SDK sources."""
import hashlib
import importlib
import importlib.metadata
import json
import os
import site
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

root = Path(sys.argv[1]).resolve()
head_pin = sys.argv[2]
product_pin = sys.argv[3]
label = sys.argv[4]
source_mode = sys.argv[5]
receipt_name = sys.argv[6]
argv = sys.argv[7:]
assert label in {"e47", "f48"}
assert source_mode in {"clean", "candidate"}
assert subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip() == head_pin
production_status = subprocess.check_output(["git", "status", "--porcelain", "--", "python/deepviz/src"], cwd=root, text=True)
if source_mode == "clean":
    assert production_status == ""
else:
    names = subprocess.check_output(["git", "diff", "--name-only", product_pin, "--", "python/deepviz/src"], cwd=root, text=True).splitlines()
    assert names == ["python/deepviz/src/deepviz/tools.py"], names
    subprocess.check_call(["git", "diff", "--check", product_pin, "--", "python/deepviz/src/deepviz/tools.py"], cwd=root)
assert argv
test = Path(argv[0]).resolve()
assert test.is_relative_to(root) and test.is_file()
sys.dont_write_bytecode = True
sys.path.insert(0, str(root / "python/deepviz/src"))
site.addsitedir(r"C:\Users\bagma\deepviz-agent-toolkit\.venv\Lib\site-packages")
origins = {}
for module_name in ("tools", "models", "normalize", "mcp_server", "recommend", "render"):
    module = importlib.import_module("deepviz." + module_name)
    path = Path(module.__file__).resolve()
    relative = path.relative_to(root).as_posix()
    assert path == root / "python/deepviz/src/deepviz" / (module_name + ".py")
    git_bytes = subprocess.check_output(["git", "show", product_pin + ":" + relative], cwd=root)
    working = path.read_bytes()
    if source_mode == "clean" or module_name != "tools":
        assert working == git_bytes
    origins[module_name] = {"path": relative, "pinned_sha256": hashlib.sha256(git_bytes).hexdigest(),
                            "working_sha256": hashlib.sha256(working).hexdigest()}
sdks = {}
for name in ("langchain_core.tools.base", "langchain_core.tools.structured", "pydantic.main"):
    module = importlib.import_module(name)
    path = Path(module.__file__).resolve()
    assert path.is_relative_to(r"C:\Users\bagma\deepviz-agent-toolkit\.venv\Lib\site-packages")
    sdks[name] = {"path": str(path), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
record = {"utc": datetime.now(UTC).isoformat(), "label": label, "source": product_pin,
          "source_mode": source_mode,
          "head": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip(),
          "branch": subprocess.check_output(["git", "branch", "--show-current"], cwd=root, text=True).strip(),
          "production_status": production_status, "test_sha256": hashlib.sha256(test.read_bytes()).hexdigest(),
          "product_module_origins": origins, "installed_sdk_origins": sdks,
          "versions": {name: importlib.metadata.version(name) for name in ("langchain-core", "pydantic", "pytest")},
          "test_args": argv}
print("R50_SOURCE_SDK_IDENTITY=" + json.dumps(record, sort_keys=True))
os.environ["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] = "1"
import pytest

exit_code = int(pytest.main(argv))
record["pytest_exit"] = exit_code
print("R50_FINAL_RECEIPT=" + json.dumps(record, sort_keys=True))
out = Path(__file__).parent / receipt_name
assert not out.exists()
out.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8", newline="\n")
raise SystemExit(exit_code)
