from __future__ import annotations
import ast
import hashlib
import json
import subprocess
from pathlib import Path

PARENT = "3185e0d9936c7d6f1a9d30b94089b804d75fe991"
HEAD = "4429f0521612b97eee3790f0d8d0fbc3cad3f8be"
ROOT = Path(__file__).resolve().parents[4]
ENGINE = "python/deepviz/src/deepviz/engines.py"
PATHS = [ENGINE, "python/deepviz/tests/test_r45_antv_subnormal_heatmap.py", "tests/r45_probes/role17/native.cjs"]
CONNECTED = ["python/deepviz/src/deepviz/render.py", "python/deepviz/src/deepviz/models.py", "python/deepviz/src/deepviz/normalize.py", "python/deepviz/tests/test_backend_antv.py"]

def git(*args: str) -> bytes:
    return subprocess.run(["git", *args], cwd=ROOT, check=True, capture_output=True).stdout

def blob(rev: str, path: str) -> bytes:
    return git("cat-file", "blob", f"{rev}:{path}")

def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def top_level(tree: ast.Module) -> list[ast.stmt]:
    return [n for n in tree.body if not (isinstance(n, ast.FunctionDef) and n.name == "_antv")]

def functions(tree: ast.Module) -> dict[str, ast.FunctionDef]:
    return {n.name: n for n in tree.body if isinstance(n, ast.FunctionDef)}

names = git("diff", "--name-status", PARENT, HEAD).decode().splitlines()
parent_engine, head_engine = blob(PARENT, ENGINE), blob(HEAD, ENGINE)
old_ast, new_ast = ast.parse(parent_engine), ast.parse(head_engine)
old_functions, new_functions = functions(old_ast), functions(new_ast)
protected = sorted(set(old_functions) - {"_antv"})
protected_equal = [name for name in protected if ast.dump(old_functions[name], include_attributes=False) == ast.dump(new_functions[name], include_attributes=False)]
assert len(protected_equal) == len(protected)
assert ast.dump(ast.Module(body=top_level(old_ast), type_ignores=[]), include_attributes=False) == ast.dump(ast.Module(body=top_level(new_ast), type_ignores=[]), include_attributes=False)
connected = {p: {rev: git("rev-parse", f"{rev}:{p}").decode().strip() for rev in (PARENT, HEAD)} for p in CONNECTED}
assert all(pair[PARENT] == pair[HEAD] for pair in connected.values())
files = {}
for path in PATHS:
    files[path] = {rev: {"git_blob": git("rev-parse", f"{rev}:{path}").decode().strip(), "sha256": digest(blob(rev, path)), "bytes": len(blob(rev, path))} for rev in (PARENT, HEAD) if subprocess.run(["git", "cat-file", "-e", f"{rev}:{path}"], cwd=ROOT, capture_output=True).returncode == 0}
report = {
    "product_parent": PARENT,
    "product_head": HEAD,
    "diff_name_status": names,
    "engine_source": {"parent": files[ENGINE][PARENT], "head": files[ENGINE][HEAD]},
    "changed_product_path_hashes": files,
    "connected_unchanged_git_blobs": connected,
    "static_ast": {"all_top_level_except__antv_identical": True, "protected_function_count": len(protected_equal), "changed_function": "_antv", "imports_and_module_level_statements_unchanged": True},
    "scope": "read-only Git blob and AST proof; no product module import, tests, scale library, native engine, browser, or output executed",
    "finite_scale_arithmetic_only": {
        "cases": [
            {"input_domain": [-1.7976931348623157e308, 1.7976931348623157e308], "safe_midpoint": 0.0, "adjacent_segment_spans": [1.7976931348623157e308, 1.7976931348623157e308], "all_finite": True},
            {"input_domain": [-1e308, 1e308], "safe_midpoint": 0.0, "adjacent_segment_spans": [1e308, 1e308], "all_finite": True}
        ],
        "method": "arithmetic derivation only; raw source values remain the color data; this is not G2/browser paint evidence"
    }
}
(ROOT / "docs/coordination/evidence/R52-21/source-proof.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
print(json.dumps(report, indent=2))

