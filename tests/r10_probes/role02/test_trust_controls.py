"""Novel finite trust controls; no browser, network, source patch, or symlink needed."""
from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

import pytest

from deepviz.mcp_server import create_server
from deepviz.tools import MAX_ARTIFACT_BYTES, ToolSession

ROWS = [{"category": "Alpha", "value": 3}, {"category": "Beta", "value": 7}]
SPEC = {"kind": "bar", "x": "category", "y": "value", "aggregation": "none"}
TABLE = {"kind": "table", "aggregation": "none"}
CANARY = b"R10_02_LOCAL_FABRICATED_HOST_CANARY"


def manifest_records(result: dict[str, Any]) -> list[dict[str, Any]]:
    path = next(Path(item) for item in result["paths"] if Path(item).name == "manifest.json")
    return json.loads(path.read_text(encoding="utf-8"))["charts"][0]["records"]


def metadata(result: Any) -> dict[str, Any]:
    blocks = result[0] if isinstance(result, tuple) else result
    return json.loads(next(block.text for block in blocks if block.type == "text"))


async def read_bytes(server: Any, uri: str) -> bytes:
    content = list(await server.read_resource(uri))[0].content
    return content.encode("utf-8") if isinstance(content, str) else content


@pytest.mark.parametrize("shape", ["row-list", "mixed-top-level", "nested-rows"])
def test_reference_shaped_data_does_not_grant_file_authority(tmp_path: Path, shape: str) -> None:
    sentinel = tmp_path / "outside.json"
    sentinel.write_bytes(CANARY)
    row = {"file": "../outside.json", "dataset_id": "not-an-issued-handle", "value": 1}
    payload = [row] if shape == "row-list" else row if shape == "mixed-top-level" else {"data": [row]}
    session = ToolSession(tmp_path / "out")  # Host deliberately grants no data_dir.
    handle = session.normalize_data(payload, TABLE)["dataset_id"]
    result = session.render_chart("echarts", {"dataset_id": handle}, TABLE)
    assert manifest_records(result) == [row]
    assert result["input_count"] == result["output_count"] == 1
    assert sentinel.read_bytes() == CANARY
    assert all(CANARY not in Path(item).read_bytes() for item in result["paths"])


@pytest.mark.parametrize("encoded", [False, True], ids=["object-ref", "json-ref"])
@pytest.mark.parametrize("revocation", ["missing", "directory"])
def test_file_backed_handles_recheck_current_file_state(
    tmp_path: Path, encoded: bool, revocation: str,
) -> None:
    root = tmp_path / "data"
    root.mkdir()
    path = root / "rows.json"
    original = json.dumps(ROWS).encode("utf-8")
    path.write_bytes(original)
    session = ToolSession(tmp_path / "out", data_dir=root)
    source: Any = {"file": "rows.json"}
    if encoded:
        source = json.dumps(source)
    first = session.normalize_data(source)["dataset_id"]
    copied = session.normalize_data(json.dumps({"dataset_id": first}))["dataset_id"]
    survivor = session.render_chart("echarts", {"dataset_id": copied}, SPEC)
    saved = {Path(item): Path(item).read_bytes() for item in survivor["paths"]}
    destinations = set(session.output_dir.iterdir())
    path.unlink()
    if revocation == "directory":
        path.mkdir()
    for handle in (first, copied):
        # Cached profiling advice is not new file authority. A render must recheck.
        assert session.recommend_chart({"dataset_id": handle})["input_count"] == len(ROWS)
        with pytest.raises(ValueError, match="File does not exist"):
            session.render_chart("echarts", {"dataset_id": handle}, SPEC)
    assert set(session.output_dir.iterdir()) == destinations
    assert all(item.read_bytes() == content for item, content in saved.items())
    if path.is_dir():
        path.rmdir()
    path.write_bytes(original)
    restored = session.render_chart("echarts", {"dataset_id": copied}, SPEC)
    assert manifest_records(restored) == ROWS
    assert set(restored["paths"]).isdisjoint(survivor["paths"])


def test_percent_encoded_filename_is_literal_not_url_decoded(tmp_path: Path) -> None:
    root = tmp_path / "data"
    root.mkdir()
    outside = tmp_path / "outside.json"
    outside.write_bytes(CANARY)
    filename = "%2e%2e%2foutside.json"
    (root / filename).write_text(json.dumps(ROWS), encoding="utf-8")
    session = ToolSession(tmp_path / "out", data_dir=root)
    result = session.render_chart("echarts", {"file": filename}, SPEC)
    assert manifest_records(result) == ROWS
    assert outside.read_bytes() == CANARY


def test_sibling_with_root_name_prefix_is_not_inside_data_root(tmp_path: Path) -> None:
    root = tmp_path / "data"
    sibling = tmp_path / "data-shadow"
    root.mkdir()
    sibling.mkdir()
    outside = sibling / "rows.json"
    outside.write_bytes(CANARY)
    session = ToolSession(tmp_path / "out", data_dir=root)
    with pytest.raises(ValueError, match="escapes"):
        session.normalize_data({"file": "../data-shadow/rows.json"})
    assert outside.read_bytes() == CANARY
    assert not session.output_dir.exists()

@pytest.mark.parametrize("unissued", ["same-leaf-file", "different-server"])
def test_only_exact_current_server_issued_resources_are_readable(tmp_path: Path, unissued: str) -> None:
    pytest.importorskip("mcp")

    async def exercise() -> None:
        root = tmp_path / "out"
        server = create_server(root)
        info = metadata(await server.call_tool("render_echarts", {"data": ROWS, "spec": SPEC}))
        resource = next(item for item in info["resources"] if item["mime_type"] == "text/html")
        issued = resource["uri"]
        original = await read_bytes(server, issued)
        if unissued == "same-leaf-file":
            artifact = next(root.rglob(Path(urlsplit(issued).path).name))
            host = artifact.parent / "host-only.json"
            host.write_bytes(CANARY)
            guessed = issued.rsplit("/", 1)[0] + "/host-only.json"
            with pytest.raises(ValueError, match="Unknown resource") as denied:
                await server.read_resource(guessed)
            assert CANARY.decode() not in str(denied.value)
            assert host.read_bytes() == CANARY
        else:
            other_server = create_server(root)  # Sharing disk grants no URI issuance.
            assert not await other_server.list_resources()
            with pytest.raises(ValueError, match="Unknown resource"):
                await other_server.read_resource(issued)
        assert len(await server.list_resources()) == len(info["resources"]) == 2
        assert await read_bytes(server, issued) == original

    asyncio.run(asyncio.wait_for(exercise(), timeout=30))


@pytest.mark.parametrize("invalid_state", ["oversize", "missing", "directory"])
def test_registered_artifacts_revalidate_before_bulk_read_and_recover(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, invalid_state: str,
) -> None:
    pytest.importorskip("mcp")
    from mcp.server.fastmcp.exceptions import ResourceError

    async def exercise() -> None:
        root = tmp_path / "out"
        server = create_server(root)
        info = metadata(await server.call_tool("render_echarts", {"data": ROWS, "spec": SPEC}))
        target = next(item["uri"] for item in info["resources"] if item["mime_type"] == "text/html")
        peer = next(item["uri"] for item in info["resources"] if item["mime_type"] == "application/json")
        artifact = next(root.rglob(Path(urlsplit(target).path).name)).resolve()
        original = artifact.read_bytes()
        peer_content = await read_bytes(server, peer)
        if invalid_state == "oversize":
            with artifact.open("wb") as stream:
                stream.truncate(MAX_ARTIFACT_BYTES + 1)  # Finite sparse local file; no large input allocation.
        else:
            artifact.unlink()
            if invalid_state == "directory":
                artifact.mkdir()
        bulk_reads: list[Path] = []
        actual_read_bytes = Path.read_bytes

        def monitored_read(path: Path) -> bytes:
            if path == artifact:
                bulk_reads.append(path)
            return actual_read_bytes(path)

        monkeypatch.setattr(Path, "read_bytes", monitored_read)
        with pytest.raises(ResourceError):
            await server.read_resource(target)
        assert not bulk_reads, "Invalid file was read before existence/type/size rejection"
        assert await read_bytes(server, peer) == peer_content
        if artifact.is_dir():
            artifact.rmdir()
        artifact.write_bytes(original)
        assert await read_bytes(server, target) == original
        assert bulk_reads == [artifact]
        assert len(await server.list_resources()) == len(info["resources"])

    asyncio.run(asyncio.wait_for(exercise(), timeout=30))
