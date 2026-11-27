"""Exact immutable AntV review identity; stdlib only, no product imports."""
from __future__ import annotations

import ast
import hashlib
import json
import subprocess
from pathlib import Path

PIN = "3185e0d9936c7d6f1a9d30b94089b804d75fe991"
ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent

def git(*args: str) -> bytes:
    return subprocess.check_output(["git", *args], cwd=ROOT)

def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def audit() -> dict:
    head = git("rev-parse", "HEAD").decode().strip()
    assert not git("diff", PIN, "HEAD", "--", "python/deepviz/src")
    parent = git("rev-parse", PIN + "^").decode().strip()
    path = "python/deepviz/src/deepviz/engines.py"
    old, new = (git("show", commit + ":" + path) for commit in (parent, PIN))
    def split(data: bytes) -> tuple[bytes, bytes, bytes]:
        start = data.index(b"def _antv(")
        stop = data.index(b"\n\ndef native_spec", start)
        return data[:start], data[start:stop], data[stop:]
    left, right = split(old), split(new)
    assert left[0] == right[0] and left[2] == right[2]
    def functions(data: bytes) -> list[tuple[str, str]]:
        text = data.decode()
        return [(node.name, ast.get_source_segment(text, node) or "") for node in ast.parse(text).body if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))]
    a, b = functions(old), functions(new)
    assert [name for name, _ in a] == [name for name, _ in b]
    protected = []
    for index, (before, after) in enumerate(zip(a, b, strict=True)):
        if before[0] != "_antv":
            assert before == after
            protected.append({"ordinal": index, "function": after[0], "sha256": digest(after[1].encode())})
    files = []
    for name in ("__init__", "models", "engines", "render", "normalize"):
        rel = "python/deepviz/src/deepviz/" + name + ".py"
        raw = (ROOT / rel).read_bytes()
        blob = git("show", PIN + ":" + rel)
        assert raw.replace(b"\r\n", b"\n") == blob
        files.append({"path": rel, "raw_sha256": digest(raw), "git_lf_sha256": digest(blob)})
    result = {"source": PIN, "review_head": head, "parent": parent, "branch": git("branch", "--show-current").decode().strip(), "changed_paths": git("diff", "--name-status", parent, PIN).decode().splitlines(), "numstat": git("diff", "--numstat", parent, PIN).decode().splitlines(), "outside_antv_prefix_exact": True, "outside_antv_suffix_exact": True, "protected_functions_byte_identical": protected, "files": files, "product_imports": 0, "tests_run": 0, "scope": "independent source review, not full branch/main approval"}
    (OUT / "source-identity.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    (OUT / "product.diff").write_bytes(git("diff", parent, PIN, "--", path))
    return result

if __name__ == "__main__":
    r = audit()
    print(json.dumps({"source": r["source"], "protected_functions": len(r["protected_functions_byte_identical"]), "prefix_suffix_exact": True, "product_imports": 0, "tests_run": 0}))
