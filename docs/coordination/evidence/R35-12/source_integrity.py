"""Read-only source identity/unchanged-code proof; imports no product modules."""
from __future__ import annotations

import ast
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
SOURCE = "85796dbe3360fb88686f2e7188122e2da80d54c2"
PARENT = "7bcfb2dcbf99f9deb44a2b5558373bd3aaccd0e6"
ENGINE = "python/deepviz/src/deepviz/engines.py"
TEST = "python/deepviz/tests/test_r23_count_channel.py"
PROTECTED = [f"python/deepviz/src/deepviz/{name}.py" for name in ("normalize", "render", "models")]
OUT = Path(__file__).resolve().parent


def git(*args: str) -> bytes:
    return subprocess.check_output(["git", *args], cwd=ROOT)


def digest(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


assert git("rev-parse", "HEAD").decode().strip() == SOURCE
assert git("rev-parse", "HEAD^").decode().strip() == PARENT
changed = git("diff", "--name-only", PARENT, SOURCE).decode().splitlines()
assert changed == [ENGINE, TEST], changed
source_files = []
for name in [ENGINE, *PROTECTED, TEST]:
    blob = git("show", f"{SOURCE}:{name}")
    working = (ROOT / name).read_bytes()
    canonical = working.replace(b"\r\n", b"\n")
    assert canonical == blob, name
    if name in PROTECTED:
        assert blob == git("show", f"{PARENT}:{name}"), name
    source_files.append({
        "path": name, "git_blob_oid": git("rev-parse", f"{SOURCE}:{name}").decode().strip(),
        "git_sha256": digest(blob), "git_bytes": len(blob),
        "working_sha256": digest(working), "working_bytes": len(working),
        "working_equal_git_after_crlf_to_lf": True,
        "equal_parent": name in PROTECTED,
    })

current = git("show", f"{SOURCE}:{ENGINE}").decode()
previous = git("show", f"{PARENT}:{ENGINE}").decode()
addition = ('    if spec.aggregation == "count" and spec.y is None and spec.kind != "heatmap":\n'
            '        y = "count"\n')
assert current.count(addition) == 1
assert current.replace(addition, "", 1) == previous
now_ast, old_ast = ast.parse(current), ast.parse(previous)
now_functions = [node for node in now_ast.body if isinstance(node, ast.FunctionDef) and node.name != "channels"]
old_functions = [node for node in old_ast.body if isinstance(node, ast.FunctionDef) and node.name != "channels"]
assert len(now_functions) == len(old_functions)
function_proofs = []
for new, old in zip(now_functions, old_functions, strict=True):
    new_text = ast.get_source_segment(current, new)
    old_text = ast.get_source_segment(previous, old)
    assert new.name == old.name and new_text == old_text
    assert ast.dump(new, include_attributes=False) == ast.dump(old, include_attributes=False)
    function_proofs.append({"name": new.name, "source_line": new.lineno,
                            "sha256": digest(new_text.encode()), "same_source_and_ast": True})
for tree in (now_ast, old_ast):
    tree.body = [node for node in tree.body if not (isinstance(node, ast.FunctionDef) and node.name == "channels")]
assert ast.dump(now_ast, include_attributes=False) == ast.dump(old_ast, include_attributes=False)

test_tree = ast.parse(git("show", f"{SOURCE}:{TEST}").decode())
coverage = []
for node in test_tree.body:
    if not isinstance(node, ast.FunctionDef) or not node.name.startswith("test_"):
        continue
    cases = 1
    for decorator in node.decorator_list:
        if isinstance(decorator, ast.Call) and isinstance(decorator.func, ast.Attribute) and decorator.func.attr == "parametrize":
            assert isinstance(decorator.args[1], (ast.List, ast.Tuple))
            cases *= len(decorator.args[1].elts)
    coverage.append({"name": node.name, "static_parameterized_cases": cases})
assert sum(item["static_parameterized_cases"] for item in coverage) == 16
diff = git("diff", "--no-ext-diff", PARENT, SOURCE, "--", ENGINE, TEST)
with (OUT / "reviewed-functional.diff").open("xb") as stream:
    stream.write(diff)
receipt = {
    "source": SOURCE, "parent": PARENT, "review_branch": "review/r35-12-count-source",
    "python": sys.version, "python_executable": sys.executable,
    "script_sha256": digest(Path(__file__).read_bytes()),
    "changed_paths_exact": changed, "source_files": source_files,
    "entire_engine_equal_parent_after_reversing_exact_two_lines": True,
    "all_nonchannels_module_ast_equal_parent": True,
    "nonchannels_functions_verified": len(function_proofs), "function_proofs": function_proofs,
    "original_new_test_static_coverage": coverage,
    "reviewed_diff_sha256": digest(diff),
    "product_modules_imported": False, "product_tests_executed": 0,
    "sdk_import_or_browser_paint_claim": False,
}
with (OUT / "source-identity.json").open("x", encoding="utf-8", newline="\n") as stream:
    stream.write(json.dumps(receipt, indent=2) + "\n")
print(json.dumps({key: value for key, value in receipt.items() if key not in {
    "function_proofs", "original_new_test_static_coverage", "source_files"
}}, indent=2))
