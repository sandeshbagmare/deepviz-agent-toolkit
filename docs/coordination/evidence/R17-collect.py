"""Collect completed R04 checks only; never run or relabel product tests."""
import hashlib
import json
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

root, artifacts, before, output = map(Path, sys.argv[1:])
source = "7bcfb2dcbf99f9deb44a2b5558373bd3aaccd0e6"
evidence = root / "docs/coordination/evidence"
assert subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip() == source
assert not output.exists(), "Refuse to overwrite an existing evidence packet"


def digest(data):
    return hashlib.sha256(data).hexdigest()


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def junit(name, expected):
    path = evidence / f"{name}.xml"
    suite = ET.parse(path).getroot().find("testsuite")
    assert suite is not None
    totals = {key: int(suite.attrib[key]) for key in ["tests", "failures", "errors", "skipped"]}
    totals["passed"] = totals["tests"] - totals["failures"] - totals["errors"] - totals["skipped"]
    assert totals == expected, (name, totals)
    outcomes = []
    for case in suite.iter("testcase"):
        for tag in ["failure", "error", "skipped"]:
            if case.find(tag) is not None:
                outcomes.append({"class": case.attrib["classname"], "name": case.attrib["name"], "outcome": tag})
    return {"file": path.name, "sha256": digest(path.read_bytes()), "totals": totals,
            "xml_seconds": float(suite.attrib["time"]), "outcomes": outcomes}


generation, browser = load(artifacts / "generation.json"), load(artifacts / "browser.json")
assert generation["source_sha"] == source and generation["tracked_source_diff"] == []
assert len(generation["cases"]) == len(browser["results"]) == 5
assert all(item["status"] == "PASS" and not item["errors"] and not item["blocked"] for item in browser["results"])
assert generation["tool"]["status"] == "rejected" and generation["tool"]["new_artifacts"] == 0
assert generation["tool"]["caller_preserved"]
before_data = load(before / "summary.json")
assert before_data["input_bytes"] == generation["tool"]["input_bytes"] == 1700
assert before_data["tracemalloc_peak"] == 30698790

paths = ["python/deepviz/src/deepviz/engines.py", "python/deepviz/src/deepviz/render.py",
         "python/deepviz/src/deepviz/normalize.py", "packages/deepviz/src/normalize.ts",
         "python/deepviz/tests/test_r12_table_budget.py", "python/deepviz/tests/test_r07_finite_overflow.py",
         "packages/deepviz/test/test_r07_finite_overflow.test.mjs"]
source_hashes = []
for name in paths:
    actual = (root / name).read_bytes()
    committed = subprocess.check_output(["git", "show", f"{source}:{name}"], cwd=root)
    assert actual.replace(b"\r\n", b"\n") == committed
    source_hashes.append({"path": name, "working_sha256": digest(actual), "git_blob_sha256": digest(committed)})

packet = {
    "source_sha": source, "scope": "Integrated milestone, not release/final-candidate acceptance",
    "source_hashes": source_hashes,
    "full_nonscale": junit("R17-integrated-nonscale", {"tests": 3084, "failures": 36, "errors": 0, "skipped": 5, "passed": 3043}),
    "focused": junit("R17-sum-integrated-nonscale", {"tests": 345, "failures": 0, "errors": 0, "skipped": 0, "passed": 345}),
    "nonscale_exclusions": 9,
    "npm": {"tests": 269, "pass": 269, "fail": 0, "skip": 0, "milliseconds": 4801.9805,
            "build_exit": 0, "typecheck_exit": 0, "schema_exit": 0, "pack_dry_run_exit": 0, "npm_ci": "NOT RUN: no installs authorized"},
    "memory_control": {"before": {k: before_data[k] for k in ["input_bytes", "input_count", "output_count", "union_fields", "native_graphics", "tracemalloc_current", "tracemalloc_peak", "elapsed_seconds"]},
        "before_source_correction": "Original probe hardcodes 0c5 source; actual unchanged loaded modules were independently verified at 5340 (3aa product bytes), see R12 report",
        "after": generation["tool"], "method": "Per-call tracemalloc Python allocations, not OS RSS/native/browser memory or a general memory ceiling"},
    "browser": {k: browser[k] for k in ["browser", "node", "resource_mode", "assets", "limits"]},
    "renders": [], "raw_local_evidence": [],
    "limits": ["36 full non-scale failures remain", "5 skips and 9 scale deselections are not passes", "Prefix-SUM accuracy R13-01-F1 remains open", "No fresh 10M/distribution/installed-consumer/green-CI/final-review approval"]}
output.mkdir(parents=True)
for item, rendered in zip(browser["results"], generation["cases"], strict=True):
    assert item["engine"] == rendered["engine"]
    png = Path(item["screenshot"]).read_bytes()
    assert digest(png) == item["sha256"]
    name = f"{item['engine']}-normal.png"
    with (output / name).open("xb") as handle:
        handle.write(png)
    packet["renders"].append({"engine": item["engine"], "status": item["status"], "observed": item["observed"],
        "image": name, "sha256": digest(png), "bytes": len(png), "opened_by_R04": True,
        "correctness": "Native and accessible table preserve headers label/value and rows A=3,B=7; no clipping in this two-row fixture"})
for name in ["R12-red.log", "R12-expanded-red.log", "R12-green.log", "R12-clean-not-scale.log",
             "R17-sum-integrated.log", "R17-integrated-nonscale.log", "R17-sum-integrated-nonscale.log",
             "R17-sum-ruff.log", "R17-sum-mypy.log", *[f"R17-npm-{key}.log" for key in ["build", "typecheck", "test", "schema", "pack"]]]:
    raw = (evidence / name).read_bytes()
    packet["raw_local_evidence"].append({"name": name, "bytes": len(raw), "sha256": digest(raw)})
with (output / "summary.json").open("x", encoding="utf-8", newline="\n") as handle:
    json.dump(packet, handle, indent=2)
    handle.write("\n")
print(json.dumps({"source": source, "full": packet["full_nonscale"]["totals"], "focused": packet["focused"]["totals"],
                  "images": len(packet["renders"]), "raw_hashes": len(packet["raw_local_evidence"])}))
