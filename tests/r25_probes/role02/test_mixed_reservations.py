"""One missing P2 boundary: real mixed 4/3/2 reservation race, not a transport replay."""
from __future__ import annotations

import asyncio
import hashlib
import importlib
import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from threading import Barrier, Lock
from types import FrameType
from typing import Any

from mcp.server.fastmcp.exceptions import ToolError

from deepviz.mcp_server import create_server
from deepviz.tools import ToolSession

ROWS = [{"category": "Alpha", "value": 3}, {"category": "Beta", "value": 7}]
SPEC = {"kind": "bar", "x": "category", "y": "value", "aggregation": "none", "title": "R25 capacity Alpha 3 / Beta 7"}


def call(server: Any, engine: str) -> dict[str, Any]:
    content = asyncio.run(server.call_tool(f"render_{engine}", {"data": ROWS, "spec": SPEC}))
    return json.loads(next(item.text for item in content if item.type == "text"))


def file_hashes(root: Path) -> dict[str, str]:
    return {path.relative_to(root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in root.rglob("*") if path.is_file()}


def resource_bytes(server: Any, uri: str) -> bytes:
    content = list(asyncio.run(server.read_resource(uri)))[0].content
    return content.encode("utf-8") if isinstance(content, str) else content


def test_mixed_static_and_html_race_preserves_existing_authority_and_early_denial(tmp_path: Path) -> None:
    source = Path(os.environ["R25_02_SOURCE"]).resolve()
    for name in ("mcp_server", "tools", "render"):
        module = importlib.import_module(f"deepviz.{name}")
        assert module.__file__ is not None
        assert Path(module.__file__).resolve() == source / "python/deepviz/src/deepviz" / f"{name}.py"
    output = tmp_path / "out"
    output.mkdir()
    host = output / "host-owned.txt"
    host.write_text("PUBLIC_R25 preserve caller file", encoding="utf-8")
    outside = tmp_path / "outside.txt"
    outside.write_text("PUBLIC_R25 outside sentinel", encoding="utf-8")
    outside_before = outside.read_bytes()
    server = create_server(output)
    first = call(server, "matplotlib")
    assert len(first["resources"]) == 4
    uri = first["resources"][0]["uri"]
    earliest = resource_bytes(server, uri)
    for _ in range(60):
        assert len(call(server, "echarts")["resources"]) == 2
    assert len(asyncio.run(server.list_resources())) == 124
    before = file_hashes(output)
    seed_png = next(output.rglob("chart.png"))
    if destination := os.environ.get("R25_02_RESULTS"):
        with (Path(destination) / "capacity-alpha-beta.png").open("xb") as png_stream:
            png_stream.write(seed_png.read_bytes())

    barrier = Barrier(4)
    entered: list[str] = []
    entry_lock = Lock()
    watched = ToolSession.render_chart.__code__

    def observe(frame: FrameType, event: str, argument: Any) -> None:
        if event == "call" and frame.f_code is watched:
            with entry_lock:
                entered.append(frame.f_locals["engine"])

    def attempt(engine: str) -> dict[str, Any]:
        previous = sys.getprofile()
        barrier.wait(timeout=20)
        sys.setprofile(observe)
        try:
            result = call(server, engine)
            return {"engine": engine, "accepted": True, "resources": result["resources"]}
        except ToolError as error:
            assert "capacity" in str(error)
            return {"engine": engine, "accepted": False, "error": str(error), "resources": []}
        finally:
            sys.setprofile(previous)

    with ThreadPoolExecutor(max_workers=4) as pool:
        outcomes = list(pool.map(attempt, ("matplotlib", "vega", "echarts", "echarts")))
    accepted = [item for item in outcomes if item["accepted"]]
    assert accepted
    added = sum(len(item["resources"]) for item in accepted)
    assert added in (3, 4)
    assert sorted(entered) == sorted(item["engine"] for item in accepted), "Denied request reached output allocation"
    assert len(asyncio.run(server.list_resources())) == 124 + added <= 128
    after = file_hashes(output)
    assert all(after.get(path) == digest for path, digest in before.items())
    assert len(after) == len(before) + added
    assert resource_bytes(server, uri) == earliest
    for item in accepted:
        assert len(item["resources"]) == {"matplotlib": 4, "vega": 3, "echarts": 2}[item["engine"]]
        for resource in item["resources"]:
            assert resource_bytes(server, resource["uri"])
    # One remaining slot is documented unusable for every current renderer; do not evict.
    stable = file_hashes(output)
    try:
        call(server, "echarts")
    except ToolError as error:
        assert "capacity" in str(error)
    else:
        raise AssertionError("A 127/128-resource server cannot reserve another two artifacts")
    assert file_hashes(output) == stable
    assert resource_bytes(server, uri) == earliest
    assert host.read_text(encoding="utf-8") == "PUBLIC_R25 preserve caller file"
    assert outside.read_bytes() == outside_before
    assert not asyncio.run(server.list_resource_templates())
    normalized = asyncio.run(server.call_tool("normalize_data", {"data": ROWS}))
    assert '"input_count": 2' in str(normalized)
    if destination:
        record = {"prefill_resources": 124, "outcomes": outcomes, "actual_render_entries": entered,
                  "added_resources": added, "final_resources": 124 + added,
                  "prior_files_hash_preserved": len(before), "earliest_resource_preserved": True,
                  "host_outside_sentinels_preserved": True, "new_output_files": len(after) - len(before),
                  "rejected_after_capacity_no_new_output": True, "ordinary_normalization_recovers": True,
                  "png_sha256": hashlib.sha256(seed_png.read_bytes()).hexdigest(),
                  "observation": "Four real SDK worker calls; read-only per-thread code-entry profile; no patch/cap change"}
        with (Path(destination) / "mixed-reservation-result.json").open("x", encoding="utf-8") as stream:
            json.dump(record, stream, indent=2)
            stream.write("\n")
