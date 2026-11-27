"""Read-only exact-Git-source identity proof for R52-14."""
import ast
import hashlib
import json
import subprocess
import sys
from pathlib import Path

repo, head, parent = Path(sys.argv[1]), sys.argv[2], sys.argv[3]

def git(*args):
    return subprocess.check_output(["git", "-C", str(repo), *args])

def engine(rev):
    return git("show", f"{rev}:python/deepviz/src/deepviz/engines.py")

head_bytes, parent_bytes = engine(head), engine(parent)
head_ast = ast.parse(head_bytes.decode("utf-8"))
parent_ast = ast.parse(parent_bytes.decode("utf-8"))

def without_antv(tree):
    return [node for node in tree.body if not
            (isinstance(node, ast.FunctionDef) and node.name == "_antv")]

same = ast.dump(ast.Module(body=without_antv(head_ast), type_ignores=[]),
                 include_attributes=False) == ast.dump(
    ast.Module(body=without_antv(parent_ast), type_ignores=[]), include_attributes=False)
changed = git("diff", "--name-status", parent, head,
              "--", "python/deepviz/src/deepviz").decode().splitlines()
function = next(node for node in head_ast.body
                if isinstance(node, ast.FunctionDef) and node.name == "_antv")
proof = {
    "source": head,
    "parent": parent,
    "changed_package_source_paths": changed,
    "all_non_antv_module_ast_equal": same,
    "non_antv_module_body_nodes_head": len(without_antv(head_ast)),
    "non_antv_module_body_nodes_parent": len(without_antv(parent_ast)),
    "head_antv_lines": [function.lineno, function.end_lineno],
    "head_engines_sha256": hashlib.sha256(head_bytes).hexdigest(),
    "parent_engines_sha256": hashlib.sha256(parent_bytes).hexdigest(),
    "only_product_python_source_change_is_antv_function":
        len(changed) == 1 and changed[0].startswith("M\t") and
        changed[0].endswith("engines.py") and same,
    "static_review_no_product_module_imports": True,
}
print(json.dumps(proof, indent=2))
