"""Tiny frozen Git fixtures only: no DeepViz imports, builds or measurements."""
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

ENVELOPE = Path(__file__).with_name("frozen_scale_envelope.py")


def api():
    assert ENVELOPE.is_file(), "NEW frozen-source envelope not implemented"
    spec = importlib.util.spec_from_file_location("role21_envelope", ENVELOPE)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def git(root, *args):
    done = subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True, check=True)
    return done.stdout.strip()


@pytest.fixture
def candidate(tmp_path):
    root = tmp_path / "tiny-candidate"
    root.mkdir()
    git(root, "init", "-q")
    files = {
        ".gitattributes": "* text=auto eol=lf\n",
        ".gitignore": "__pycache__/\nignored/\n",
        "pyproject.toml": "# Synthetic config; no production package\n",
        "python/deepviz/src/deepviz/__init__.py": "# NOT DeepViz\n",
        "python/deepviz/src/deepviz/models.py": "# synthetic model sentinel\n",
        "python/deepviz/src/deepviz/normalize.py": "# synthetic normalizer sentinel\n",
        "tests/test_sentinel.py": "def test_fixture_only(): assert True\n",
        "scripts/performance_suite.py": "# synthetic runner sentinel; not a benchmark\n",
    }
    for name, text in files.items():
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8", newline="\n")
    commit(root)
    return root


def commit(root):
    git(root, "add", ".")
    git(root, "-c", "user.name=OfflineFixture", "-c", "user.email=fixture@example.invalid",
        "commit", "-qm", "Synthetic envelope fixture only")
    return git(root, "rev-parse", "HEAD")


def test_clean_plan_executes_nothing_and_is_not_green(candidate, tmp_path):
    module = api()
    result = module.verify(candidate, git(candidate, "rev-parse", "HEAD"), tmp_path / "evidence")
    assert result["status"] == "PLAN_ONLY_NOT_EXECUTED"
    assert result["commands_executed"] == 0
    assert result["measurement_verified"] is False
    assert not (tmp_path / "evidence").exists()
    assert str(candidate / "scripts/performance_suite.py") in result["command"]


@pytest.mark.parametrize("mutation", ["runner", "normalizer", "test", "config", "head", "untracked"])
def test_freeze_rejects_changes(candidate, mutation):
    module = api()
    pin = git(candidate, "rev-parse", "HEAD")
    before = module.freeze(candidate, pin, {})
    paths = {"runner": "scripts/performance_suite.py", "normalizer": "python/deepviz/src/deepviz/normalize.py",
             "test": "tests/test_sentinel.py", "config": "pyproject.toml", "untracked": "unexpected.json"}
    path = candidate / paths.get(mutation, "pyproject.toml")
    path.write_text("changed fixture bytes\n", encoding="utf-8")
    if mutation == "head":
        commit(candidate)
    with pytest.raises(ValueError):
        after = module.freeze(candidate, pin, {})
        module.same_source(before, after)


def test_wrong_sha_and_skipped_worktree_flags_fail_closed(candidate):
    module = api()
    with pytest.raises(ValueError):
        module.freeze(candidate, "0" * 40, {})
    git(candidate, "update-index", "--assume-unchanged", "python/deepviz/src/deepviz/normalize.py")
    (candidate / "python/deepviz/src/deepviz/normalize.py").write_text("hidden dirty\n")
    with pytest.raises(ValueError):
        module.freeze(candidate, git(candidate, "rev-parse", "HEAD"), {})


def test_explicit_data_input_is_hashed_but_never_executed(candidate):
    import hashlib
    module = api()
    data = candidate / "allowed.json"
    data.write_bytes(b"[]\n")
    allowed = {"allowed.json": hashlib.sha256(data.read_bytes()).hexdigest()}
    pin = git(candidate, "rev-parse", "HEAD")
    before = module.freeze(candidate, pin, allowed)
    module.same_source(before, module.freeze(candidate, pin, allowed))
    data.write_bytes(b"[1]\n")
    with pytest.raises(ValueError):
        module.freeze(candidate, pin, allowed)


@pytest.mark.parametrize("shadow", ["deepviz/__init__.py", "scripts/deepviz.py", "scripts/sitecustomize.py"])
def test_even_ignored_import_shadows_fail_closed(candidate, shadow):
    module = api()
    path = candidate / shadow
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("# ignored shadow sentinel\n")
    with (candidate / ".gitignore").open("a") as stream:
        stream.write(shadow + "\n")
    commit(candidate)
    with pytest.raises(ValueError):
        module.freeze(candidate, git(candidate, "rev-parse", "HEAD"), {})


def test_report_missing_is_never_a_pass(candidate, tmp_path):
    module = api()
    result = module.verify(candidate, git(candidate, "rev-parse", "HEAD"), tmp_path / "evidence", run=True)
    assert result["status"] == "REJECTED_NOT_SCALE_APPROVAL"
    assert "report" in result["error"].lower()
    assert result["commands_executed"] == 1
    assert result["measurement_verified"] is False
    assert json.loads((tmp_path / "evidence/result.json").read_text())["status"] == result["status"]


def matrix(before):
    """Handcrafted metadata ONLY; no rows generated/consumed or peaks measured."""
    source = {"root": before["root"], "commit": before["head"],
              "dirty_paths": before["reported_dirty_paths"], "sha256": dict(before["python_sha256"])}
    rows = []
    for case in ["numeric_sample", "category_sum", "category_mean"]:
        for count in [10, 1000, 100000, 1000000, 10000000]:
            for repeat in ([1, 2] if case == "numeric_sample" else [1]):
                rows.append({"case": case, "count": count, "repeat": repeat, "status": "passed",
                             "source": source, "input_count": count, "consumed_count": count,
                             "source_exhausted": True, "max_points": 2000,
                             "output_count": min(count, 2000) if case == "numeric_sample" else 7})
    return {"synthetic_fixture_not_measurement": True, "status": "passed", "errors": [],
            "source": source, "harness": source, "requested_counts": [10, 1000, 100000, 1000000, 10000000],
            "requested_cases": ["numeric_sample", "category_sum", "category_mean"],
            "numeric_repeats": 2, "render_counts": [], "results": rows}


@pytest.mark.parametrize("mutation", ["allskip", "wrongcount", "incomplete", "wronghash", "dirty",
                                       "errors", "harness", "repeat", "wrong-source"])
def test_metadata_rejects_skips_wrong_counts_and_source(candidate, mutation):
    module = api()
    before = module.freeze(candidate, git(candidate, "rev-parse", "HEAD"), {})
    data = matrix(before)
    if mutation == "allskip":
        for row in data["results"]:
            row["status"] = "skipped"
    elif mutation == "wrongcount":
        data["results"][0]["consumed_count"] = 9
    elif mutation == "incomplete":
        data["results"].pop()
    elif mutation == "wronghash":
        data["source"]["sha256"]["python/deepviz/src/deepviz/normalize.py"] = "0" * 64
    elif mutation == "dirty":
        data["source"]["dirty_paths"] = [" M scripts/performance_suite.py"]
    elif mutation == "errors":
        data["errors"] = ["synthetic child failure"]
    elif mutation == "harness":
        data["harness"] = {}
    elif mutation == "repeat":
        data["results"][1]["repeat"] = 1
    else:
        data["source"]["commit"] = "0" * 40
    with pytest.raises(ValueError):
        module.validate_matrix(data, before)


def test_synthetic_metadata_positive_is_not_measurement_proof(candidate):
    module = api()
    before = module.freeze(candidate, git(candidate, "rev-parse", "HEAD"), {})
    assert module.validate_matrix(matrix(before), before) == 20


@pytest.mark.parametrize("change", ["runner", "normalizer", "head", "skip", "none"])
def test_fixed_child_command_checks_after_and_real_receipt(candidate, tmp_path, change):
    module = api()
    runner = candidate / "scripts/performance_suite.py"
    # Fixed runner path with an explicitly synthetic fixture program, not DeepViz.
    code = "import argparse,hashlib,json,subprocess;from pathlib import Path\n"
    code += "p=argparse.ArgumentParser();p.add_argument('--output');a,_=p.parse_known_args()\n"
    code += "r=Path(__file__).resolve().parents[1]\n"
    if change == "runner":
        code += "with Path(__file__).open('a') as f:f.write('# changed runner fixture\\n')\n"
    elif change == "normalizer":
        code += "(r/'python/deepviz/src/deepviz/normalize.py').write_text('# changed fixture')\n"
    elif change == "head":
        code += "subprocess.run(['git','-C',str(r),'-c','user.name=OfflineFixture','-c','user.email=fixture@example.invalid','commit','--allow-empty','-qm','Changed fixture HEAD'],check=True)\n"
    payload = matrix(module.freeze(candidate, git(candidate, "rev-parse", "HEAD"), {}))
    # HEAD/module hashes will be completed AFTER this runner has been committed.
    code += "d=json.loads(" + repr(json.dumps(payload)) + ")\n"
    code += "s={'root':str(r),'commit':subprocess.check_output(['git','-C',str(r),'rev-parse','HEAD'],text=True).strip(),'dirty_paths':subprocess.check_output(['git','-C',str(r),'status','--porcelain'],text=True).splitlines(),'sha256':{x.relative_to(r).as_posix():hashlib.sha256(x.read_bytes()).hexdigest() for x in (r/'python/deepviz/src/deepviz').rglob('*.py')}}\n"
    code += "d['source']=s;d['harness']=s\nfor row in d['results']:row['source']=s\n"
    if change == "skip":
        code += "for row in d['results']:row['status']='skipped'\n"
    code += "Path(a.output).write_text(json.dumps(d))\n"
    runner.write_text(code, encoding="utf-8", newline="\n")
    pin = commit(candidate)
    result = module.verify(candidate, pin, tmp_path / "evidence", run=True)
    assert result["commands_executed"] == 1
    assert result["measurement_verified"] is False
    expected = "PROVENANCE_AND_COUNTS_PASS_NOT_SCALE_APPROVAL" if change == "none" else "REJECTED_NOT_SCALE_APPROVAL"
    assert result["status"] == expected, result
    assert "not attested" in result["module_origin_limit"]


def test_prior_external_evidence_is_preserved(candidate, tmp_path):
    module = api()
    directory = tmp_path / "evidence"
    directory.mkdir()
    sentinel = directory / "caller.txt"
    sentinel.write_text("preserve caller")
    with pytest.raises(ValueError):
        module.verify(candidate, git(candidate, "rev-parse", "HEAD"), directory, run=True)
    assert sentinel.read_text() == "preserve caller"


def test_output_inside_checkout_is_rejected_even_plan(candidate):
    with pytest.raises(ValueError):
        api().verify(candidate, git(candidate, "rev-parse", "HEAD"), candidate / "unsafe-output")


@pytest.mark.parametrize("kind", ["tracked", "ignored"])
def test_explicit_tracked_or_ignored_data_is_frozen(candidate, kind):
    import hashlib
    module = api()
    name = "data.csv" if kind == "tracked" else "ignored/data.csv"
    data = candidate / name
    data.parent.mkdir(parents=True, exist_ok=True)
    data.write_bytes(b"x,y\n1,2\n")
    if kind == "tracked":
        commit(candidate)
    allowed = {name: hashlib.sha256(data.read_bytes()).hexdigest()}
    pin = git(candidate, "rev-parse", "HEAD")
    before = module.freeze(candidate, pin, allowed)
    module.same_source(before, module.freeze(candidate, pin, allowed))
    data.write_bytes(b"changed input")
    with pytest.raises(ValueError):
        module.freeze(candidate, pin, allowed)


def test_report_integer_fields_do_not_accept_float_counts(candidate):
    module = api()
    before = module.freeze(candidate, git(candidate, "rev-parse", "HEAD"), {})
    data = matrix(before)
    data["results"][0]["count"] = 10.0
    with pytest.raises(ValueError):
        module.validate_matrix(data, before)


@pytest.mark.parametrize("name", ["../external.json", "scripts/allowed.py", "allowed.pth"])
def test_allowlist_never_grants_path_traversal_or_code(candidate, name):
    with pytest.raises(ValueError):
        api().freeze(candidate, git(candidate, "rev-parse", "HEAD"), {name: "0" * 64})


def test_cli_plan_has_zero_execution_and_rejects_arbitrary_command(candidate, tmp_path):
    argv = [sys.executable, str(ENVELOPE), str(candidate), git(candidate, "rev-parse", "HEAD"),
            str(tmp_path / "external-evidence")]
    done = subprocess.run(argv, capture_output=True, text=True, timeout=20)
    assert done.returncode == 0, done.stderr
    plan = json.loads(done.stdout)
    assert plan["commands_executed"] == 0
    assert plan["status"] == "PLAN_ONLY_NOT_EXECUTED" and plan["measurement_verified"] is False
    assert not (tmp_path / "external-evidence").exists()
    bad = subprocess.run([*argv, "--command", "echo fake"], capture_output=True, text=True, timeout=20)
    assert bad.returncode == 2
    assert not (tmp_path / "external-evidence").exists()


def test_large_report_is_bounded_before_json_load(candidate, tmp_path):
    runner = candidate / "scripts/performance_suite.py"
    runner.write_text("import argparse\nfrom pathlib import Path\np=argparse.ArgumentParser();p.add_argument('--output');a,_=p.parse_known_args();Path(a.output).write_bytes(b' '* (4*1024**2+1))\n", newline="\n")
    pin = commit(candidate)
    result = api().verify(candidate, pin, tmp_path / "evidence", run=True)
    assert result["status"] == "REJECTED_NOT_SCALE_APPROVAL"
    assert "4 MiB" in result["error"]


def test_nonzero_child_exit_never_passes(candidate, tmp_path):
    runner = candidate / "scripts/performance_suite.py"
    runner.write_text("raise SystemExit(3)\n", newline="\n")
    pin = commit(candidate)
    result = api().verify(candidate, pin, tmp_path / "evidence", run=True)
    assert result["status"] == "REJECTED_NOT_SCALE_APPROVAL" and result["exit"] == 3
    assert result["commands_executed"] == 1 and result["measurement_verified"] is False
