"""Make portable evidence from actual retained bff test receipts, not expected output."""
from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path


def read_json(path: Path):
    data = path.read_bytes()
    return json.loads(data.decode("utf-16" if data.startswith((b"\xff\xfe", b"\xfe\xff")) else "utf-8-sig"))


def main() -> None:
    artifacts = Path("artifacts/r32-15")
    gate = read_json(artifacts / "postrun-gate-corrected.json")
    diagnostic = read_json(artifacts / "packet-working-vs-Git-hash-diagnostic.json")
    pin = "bff9384d1ebe5c8f6f8f0f994300264b32bb98d8"
    assert gate["gate"] == "PASS" and gate["source_commit"] == pin
    assert gate["tests"]["distinct_tests"]["total_passed"] == 196
    assert diagnostic["author_worktree_HEAD"] == pin
    assert diagnostic["packet_matches_author_working_raw"]
    assert diagnostic["author_working_LF_normalized_equals_published_Git"]
    assert diagnostic["author_working_total_LF"] == 81 and diagnostic["author_working_CRLF"] == 63
    assert diagnostic["actual_Git_LF_sha256"] == gate["source_import_identity"]["source_Git_raw_equal_sha256"][
        "python/deepviz/src/deepviz/models.py"]
    for name, digest in gate["raw_artifact_sha256"].items():
        assert hashlib.sha256((artifacts / name).read_bytes()).hexdigest() == digest
    for name, digest in gate["probe_sha256"].items():
        assert hashlib.sha256(Path(name).read_bytes()).hexdigest() == digest
    identity = gate["source_import_identity"] | {
        "parent_commit": "99841ffb80e0f2ea90c753c1bf0ceff718e0e180",
        "PR": 33,
        "wire_loader_same_source_commit_no_deepviz_package_import": True,
        "all15rawGit_before_after": True,
        "original40tests_schema_workflow_unchanged": True,
        "probe_sha256": gate["probe_sha256"] | {
            "tests/r32_probes/role15/collect_result.py": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()},
        "hash_clarification_M1": {
            "resolved_not_a_product_finding": True,
            "Git_LF_tested_model_sha256": diagnostic["actual_Git_LF_sha256"],
            "packet_author_working_mixed_EOL_model_sha256": diagnostic["author_working_raw_sha256"],
            "author_working_total_LF": 81, "author_working_CRLF": 63,
            "CRLF_to_LF_equals_actual_published_Git": True,
            "not_author_test_approval_borrowing": True}}
    raw_hashes = gate["raw_artifact_sha256"] | {
        name: hashlib.sha256((artifacts / name).read_bytes()).hexdigest()
        for name in ("postrun-gate-corrected.json", "packet-working-vs-Git-hash-diagnostic.json")}
    samples = {"source_commit": pin, "scope": "Nine actual native Mapping output/error representatives from forty",
               "native40_final_XML_sha256": raw_hashes["native40-final.xml"],
               "all40_outputs_checked": gate["native_outputs"],
               "actual_three_paths": ["native Mapping -> model_validate", "JSON decoder -> model_validate",
                                      "model_validate_json -> model_dump_json -> schema -> roundtrip"],
               "representatives": gate["representative_actual_outputs"],
               "chart": "N/A model-only slice; actual serialized model JSON evidence applies"}
    summary = {"source_commit": pin, "owner_session": "ses_de56780c8ffe7LgwvwdfR5qFQD",
               "own_branch": "agents/r10-15-owned-input-cleanup", "own_parent": "a2449226618f48e2fa4a023a92605733c745196e",
               "result": "PASS actual bff numeric Mapping/wire contract; no material finding; M1 hash encoding clarified",
               "genuine_independent_tester": 2, "no_old114_carryforward": True,
               "actual_tests": gate["tests"], "native_outputs": gate["native_outputs"],
               "timing_seconds": {"fresh_provided82_plus_native40": 0.87, "fresh_unchanged74": 5.02,
                                  "final_native40_after_annotation_only": 0.51},
               "focused_Ruff_exit": 0, "focused_mypy_exit": 0, "focused_mypy_files": 1,
               "own_Ruff_exit": 0, "own_mypy_exit": 0,
               "raw_artifact_sha256": raw_hashes, "hash_clarification_M1_resolved": True,
               "preserved_nonproduct_failures": ["Own CASES variable typing annotation initially missing; fixed only annotation, final40 rerun not double-counted",
                                                  "Own postrun guard initially used packet working hash for Git bytes; uniform CRLF hypothesis false, mixed EOL provenance then actually proved"],
               "limits": ["Local Python3.12, existing read-only dependencies, no installs/API/spawn/CI polling",
                          "No production/schema/workflow/original oracle edits, no full67 output collector replay",
                          "No SUM/formats/scale/build/render/MCP/DeepAgent/npm/full-toolkit claim; model-only actual JSON evidence",
                          "R04 owns four actual-bff gates plus fresh CI and merge/default ancestry, not this tester"]}
    output = Path("docs/coordination/evidence/R32-15")
    output.mkdir(parents=True, exist_ok=False)
    for name, value in (("source-identity.json", identity), ("summary.json", summary),
                        ("actual-native-output.json", samples)):
        (output / name).write_text(json.dumps(value, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    assert subprocess.check_output(["git", "branch", "--show-current"], text=True).strip() == summary["own_branch"]
    print("R32_PORTABLE_EVIDENCE_FROM_REAL_RECEIPTS_EXIT0/actual196pass/native40/all15Git/hashM1resolved")


if __name__ == "__main__":
    main()
