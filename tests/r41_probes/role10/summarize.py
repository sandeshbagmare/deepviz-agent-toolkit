"""Collect immutable evidence; collector exit0 is NOT a product acceptance pass."""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import re
import shutil
import subprocess
import xml.etree.ElementTree as ET
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def xml_cases(path: Path) -> list[dict[str, Any]]:
    result = []
    for case in ET.parse(path).getroot().iter("testcase"):
        failure = case.find("failure")
        error = case.find("error")
        skip = case.find("skipped")
        result.append({"class": case.get("classname", ""), "name": case.get("name"),
                       "outcome": "failure" if failure is not None else "error" if error is not None else "skip" if skip is not None else "pass",
                       "message": failure.get("message", "")[:1200] if failure is not None else ""})
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("bindings", type=Path)
    parser.add_argument("evidence", type=Path)
    args = parser.parse_args()
    binding_path, destination = args.bindings.resolve(), args.evidence.resolve()
    root = binding_path.parent
    data = json.loads(binding_path.read_text(encoding="utf-8"))
    assert data["source_sha"] == "546c25ea75ee9d8a41b3832aa639664bc9a683b5"
    source = Path(data["source_root"])
    assert subprocess.check_output(["git", "-C", str(source), "rev-parse", "HEAD"], text=True).strip() == data["source_sha"]
    assert not subprocess.check_output(["git", "-C", str(source), "status", "--porcelain"])
    for key in ("current", "base", "oracles", "built", "compiler"):
        for item in data[key]:
            assert digest(Path(item["path"])) == item["sha256"], item["path"]
            if key in ("current", "base", "oracles"):
                original = subprocess.check_output(["git", "-C", str(source), "show", item["Git_commit"] + ":" + item["relative"]])
                assert hashlib.sha256(original).hexdigest() == item["sha256"]
    destination.mkdir(parents=True, exist_ok=False)
    primary = xml_cases(root / "python-semantics.xml")
    policy = xml_cases(root / "known-policy-red.xml")
    positive = xml_cases(root / "python-ownership-positive.xml")
    assert len(primary) == 251 and sum(case["outcome"] == "pass" for case in primary) == 239
    assert len(policy) == 4 and all(case["outcome"] == "failure" for case in policy)
    assert len(positive) == 2 and all(case["outcome"] == "pass" for case in positive)
    cohorts: dict[str, dict[str, int]] = {}
    for case in primary:
        group = case["class"] or "OWN-new-literal-diagnostics"
        counts = cohorts.setdefault(group, {"pass": 0, "failure": 0, "error": 0, "skip": 0})
        counts[case["outcome"]] += 1
    text = (root / "node-bound.stdout.log").read_text(encoding="utf-8")
    node_cases = [{"name": name, "outcome": "pass" if state == "ok" else "failure"}
                  for state, name in re.findall(r"^(ok|not ok) \d+ - (.+)$", text, re.MULTILINE)]
    assert len(node_cases) == 257 and sum(case["outcome"] == "pass" for case in node_cases) == 249
    node_cohorts: dict[str, dict[str, int]] = {}
    for case in node_cases:
        name = case["name"]
        group = "OWN-new-literal-diagnostics" if name.startswith("new ") else "GP" if name.startswith((
            "cross-page-empty-repeat:", "late-invalid-after-prefix-and-empty:", "late-multiple-connections-no-implicit-merge:",
            "DEDUP-R10-01-F1", "minimal-valid-control:", "direct-error-only-envelope-control:", "ordinary-business-errors-field")) else "prefix" if name.startswith((
            "exact independent oracle ", "one async group ", "mean and deterministic sampling ", "true -1 overflow ", "true 1 overflow ")) else "producer"
        counts = node_cohorts.setdefault(group, {"pass": 0, "failure": 0})
        counts[case["outcome"]] += 1
    assert node_cohorts == {"OWN-new-literal-diagnostics": {"pass": 15, "failure": 8},
                            "producer": {"pass": 98, "failure": 0}, "prefix": {"pass": 63, "failure": 0}, "GP": {"pass": 73, "failure": 0}}
    own = Path(__file__).resolve().parent
    for name in ("test_literals.py", "literals.test.mjs", "node_gate.mjs"):
        assert (own / name).read_bytes() == (root.parent / "first-code" / name).read_bytes(), name
    for path in own.glob("*.py"):
        ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    for label in ("python-semantics", "python-ownership-positive", "known-policy-red"):
        proof = json.loads((root / (label + "-proof.json")).read_text(encoding="utf-8"))
        assert proof["before"]["no_site"] == proof["after"]["no_site"] == 1
        assert proof["before"]["loaded_modules"] == proof["after"]["loaded_modules"]
    base_proof = json.loads((root / "base-child-proof.json").read_text(encoding="utf-8"))
    assert base_proof["before"]["no_site"] == base_proof["after"]["no_site"] == 1
    node_proofs = sorted((root / "node-proofs").glob("*.json"))
    assert len(node_proofs) == 4
    paths = [binding_path, *root.glob("*.log"), *root.glob("*.xml"), *root.glob("*-proof.json"),
             root / "actual-runs.json", root / "node-resume-runs.json", *node_proofs,
             root.parent / "first-code-hashes.json", root.parent / "final-quality.log"]
    copied = []
    for original in paths:
        relative = "node-proofs/" + original.name if original.parent.name == "node-proofs" else original.name
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(original, target)
        assert digest(target) == digest(original)
        copied.append({"path": relative, "bytes": target.stat().st_size, "sha256": digest(target)})
    modules = [item for item in data["current"] if item["relative"].endswith(("normalize.py", "normalize.ts"))]
    modules += [item for item in data["built"] if item["path"].startswith(data["candidate"]) and item["path"].endswith("normalize.js")]
    summary = {"UTC": datetime.now(UTC).isoformat(), "owner": "ses_de56782e3ffeI5D4lzsNVeLcDk",
               "product_sha": data["source_sha"], "scope": "independent exact546 selected normalization; NOT final/main acceptance",
               "source_clean": True, "all_input_oracle_emit_compiler_hashes_still_match": True,
               "all_13_original_external_oracle_files_match_original_Git": True,
               "all_first_literal_assertions_and_data_byte_unchanged": True,
               "module_SHA256": modules, "python_per_cohort": cohorts, "node_per_cohort": node_cohorts,
               "python_cases": primary, "node_cases": node_cases, "positive_cases": positive, "known_policy_cases": policy,
               "independent_unchanged_passes": 460, "additional_actual_ownership_passes": 2,
               "failure_disposition": {"over_strict_own_empty_warning_assumptions_not_product_bugs": 14,
                    "previously_disclosed_python_AUTO_pages_question": 2,
                    "selected_record_protocol_cells_contract_question_R04_owner_one_family": 4,
                    "unchanged_fieldname4096_vs65536_policy_R04_owner": 4},
               "initial_Node": "4 FILE-level Windows --import path errors BEFORE consumers; 0 consumer assertions; preserved",
               "overall": "RED; R04 boundary/field-policy disposition required; no oracle/source repair here",
               "limits": ["No GitHub API/PR/currentCI/main merge verification", "No npm fullsuite/pack/install or Python distribution build",
                          "No COUNT/MCP/10M/cost/format-matrix/browser/provider replay", "Zero selected skips does not prove symlink privilege or optional Arrow/Parquet coverage"],
               "copied_evidence_files": copied}
    (destination / "verification.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"collector_exit0_is_assembly_only": True, "overall": "RED", "independent_unchanged_PASS": 460,
                      "positive_ownership_PASS": 2, "copied_files": len(copied), "verification_sha256": digest(destination / "verification.json"),
                      "module_SHA256": modules}, indent=2))


if __name__ == "__main__":
    main()
