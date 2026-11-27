"""Deterministic request ownership, not a blanket native thread-safety claim."""
from __future__ import annotations

import asyncio
import importlib
import json
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from threading import Barrier, Event

import pytest

from deepviz.models import Artifact
from deepviz.tools import ToolSession, create_tools

TIMEOUT = 30  # Deadlock bound only; events, not elapsed time, determine ordering.
ROWS = [{"category": "Alpha", "amount": 2}, {"category": "Beta", "amount": 5}]
SPEC = {"kind": "bar", "x": "category", "y": "amount", "aggregation": "sum"}


def snapshot(root: Path) -> dict[str, bytes]:
    return {str(path.relative_to(root)): path.read_bytes() for path in root.rglob("*") if path.is_file()}


def seed_host_files(root: Path) -> dict[str, bytes]:
    root.mkdir()
    (root / "host-sentinel.bin").write_bytes(b"host-owned\x00\xff")
    previous = root / "echarts-host-owned" / "nested"
    previous.mkdir(parents=True)
    (previous / "successful-resource.bin").write_bytes(b"existing successful resource\x00\xff")
    return snapshot(root)


def request_caller(api: str, root: Path):
    if api == "structured-tool":
        pytest.importorskip("langchain_core")
        tool = next(tool for tool in create_tools(root) if tool.name == "render_echarts")

        def call(role):
            return tool.invoke({"data": ROWS, "spec": {**SPEC, "title": role}})

    else:
        session = ToolSession(root)
        sessions = {role: session if api == "shared-session" else ToolSession(root)
                    for role in ("survivor", "interrupted")}

        def call(role):
            return sessions[role].render_chart("echarts", ROWS, {**SPEC, "title": role})

    return call


@pytest.mark.parametrize("api", ["shared-session", "separate-sessions", "structured-tool"])
@pytest.mark.parametrize("outcome", ["exception", "cancelled-error", "escaped-peer-path"])
@pytest.mark.parametrize("first", ["survivor", "interrupted"])
def test_partial_request_cleanup_never_deletes_peer_or_host(tmp_path, monkeypatch, api, outcome, first):
    """Cancellation here is a renderer-raised BaseException, not thread preemption."""
    root = tmp_path / "shared-output"
    host = seed_host_files(root)
    rendezvous = Barrier(3)
    gates = {role: Event() for role in ("survivor", "interrupted")}
    destinations = {}

    def artifact(path):
        return Artifact(paths=[str(path)], mime_type="application/octet-stream", engine="echarts",
                        input_count=2, output_count=2, strategy="none")

    def trusted_fault_renderer(data, spec, *, engine, output_dir):
        # Inject only this trusted boundary; ToolSession's allocation/cleanup is real.
        assert data == ROWS and engine == "echarts"
        role = spec.title
        destination = Path(output_dir)
        destinations[role] = destination
        nested = destination / "nested"
        nested.mkdir()
        resource = nested / "resource.bin"
        resource.write_bytes(f"partial:{role}".encode())
        rendezvous.wait(timeout=TIMEOUT)
        assert gates[role].wait(timeout=TIMEOUT), f"unreleased {role} request"
        if role == "interrupted":
            if outcome == "cancelled-error":
                raise asyncio.CancelledError("injected renderer cancellation")
            if outcome == "exception":
                raise ValueError("injected partial failure")
            return artifact(destinations["survivor"] / "nested" / "resource.bin")
        resource.write_bytes(b"completed survivor resource\x00\xff")
        return artifact(resource)

    monkeypatch.setattr(importlib.import_module("deepviz.render"), "render", trusted_fault_renderer)
    call = request_caller(api, root)
    expected_type, message = {
        "exception": (ValueError, "injected partial failure"),
        "cancelled-error": (asyncio.CancelledError, "injected renderer cancellation"),
        "escaped-peer-path": (ValueError, "escaped the allowed output directory"),
    }[outcome]
    results = {}

    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = {role: executor.submit(call, role) for role in gates}
        try:
            rendezvous.wait(timeout=TIMEOUT)
            assert len(set(destinations.values())) == 2
            assert all(path.parent == root.resolve() for path in destinations.values())
            assert all(path.name.startswith("echarts-") for path in destinations.values())
            partial = {role: snapshot(path) for role, path in destinations.items()}
            for role in (first, "interrupted" if first == "survivor" else "survivor"):
                gates[role].set()
                if role == "interrupted":
                    with pytest.raises(expected_type, match=message):
                        futures[role].result(timeout=TIMEOUT)
                    assert not destinations[role].exists()
                else:
                    results[role] = futures[role].result(timeout=TIMEOUT)
                if role == first:
                    peer = "interrupted" if role == "survivor" else "survivor"
                    assert not futures[peer].done()  # Peer remains behind its unreleased event.
                    assert snapshot(destinations[peer]) == partial[peer]
        finally:
            for gate in gates.values():
                gate.set()

    survivor = destinations["survivor"] / "nested" / "resource.bin"
    assert results["survivor"]["paths"] == [str(survivor)]
    assert survivor.read_bytes() == b"completed survivor resource\x00\xff"
    assert snapshot(root) == {**host, str(survivor.relative_to(root)): survivor.read_bytes()}
    assert set(root.iterdir()) == {root / "host-sentinel.bin", root / "echarts-host-owned",
                                  destinations["survivor"]}


def test_distinct_real_structured_tools_share_root_without_cross_contamination(tmp_path, monkeypatch):
    """Real Agg + ECharts artifact construction; no browser/native-wide certification."""
    pytest.importorskip("langchain_core")
    image_module = pytest.importorskip("PIL.Image")
    root = tmp_path / "shared-output"
    host = seed_host_files(root)
    tools = {tool.name: tool for tool in create_tools(root)}
    original_render = importlib.import_module("deepviz.render").render
    rendezvous = Barrier(3)
    destinations = {}

    def synchronized_real_render(data, spec, *, engine, output_dir):
        destinations[engine] = Path(output_dir)
        rendezvous.wait(timeout=TIMEOUT)
        return original_render(data, spec, engine=engine, output_dir=output_dir)

    monkeypatch.setattr(importlib.import_module("deepviz.render"), "render", synchronized_real_render)
    inputs = {
        "matplotlib": [{"category": "Alpha", "amount": 2}, {"category": "Alpha", "amount": 5},
                       {"category": "Beta", "amount": -3}],
        "echarts": [{"category": "Delta", "amount": 17}, {"category": "Epsilon", "amount": 4}],
    }
    expected = {
        "matplotlib": [{"category": "Alpha", "amount": 7}, {"category": "Beta", "amount": -3}],
        "echarts": [{"category": "Delta", "amount": 17}, {"category": "Epsilon", "amount": 4}],
    }
    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = {
            engine: executor.submit(tools[f"render_{engine}"].invoke, {
                "data": data, "spec": {**SPEC, "title": f"N13 real {engine}", "width": 480, "height": 320},
            }) for engine, data in inputs.items()
        }
        rendezvous.wait(timeout=TIMEOUT)
        results = {engine: future.result(timeout=TIMEOUT) for engine, future in futures.items()}

    assert len(set(destinations.values())) == 2
    all_paths = set()
    for engine, result in results.items():
        paths = {Path(value) for value in result["paths"]}
        assert not paths & all_paths
        all_paths.update(paths)
        assert all(path.is_file() and path.is_relative_to(destinations[engine]) for path in paths)
        manifest = json.loads(next(path for path in paths if path.name == "manifest.json").read_text())
        chart = manifest["charts"][0]
        assert result["engine"] == manifest["engine"] == engine
        assert result["input_count"] == chart["input_count"] == len(inputs[engine])
        assert result["output_count"] == chart["output_count"] == 2
        assert chart["records"] == expected[engine]
        assert chart["spec"]["title"] == f"N13 real {engine}"
        if engine == "matplotlib":
            with image_module.open(next(path for path in paths if path.suffix == ".png")) as image:
                assert image.size == (480, 320)
                image.verify()
            svg = next(path for path in paths if path.suffix == ".svg")
            assert ET.parse(svg).getroot().tag == "{http://www.w3.org/2000/svg}svg"
        else:
            assert manifest["native_specs"][0]["series"][0]["data"] == [["Delta", 17], ["Epsilon", 4]]

    assert snapshot(root) == {**host, **{
        str(path.relative_to(root)): path.read_bytes() for path in all_paths
    }}
    assert set(root.iterdir()) == {root / "host-sentinel.bin", root / "echarts-host-owned",
                                  *destinations.values()}
