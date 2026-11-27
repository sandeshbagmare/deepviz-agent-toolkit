"""Proposed lifetime policy: 128 issued resource slots, fail before further generation.

128 is an explicit acceptance proposal, not an existing API guarantee. RED must stay
RED until an eligible producer implements/reviews a bounded policy. SDK objects and
stdio transport/render/files/resources below are real; no registry/parser mutation.
"""
from __future__ import annotations

import asyncio
import hashlib
import json
import sys
from datetime import timedelta
from pathlib import Path

import pytest

from deepviz.mcp_server import create_server
from deepviz.tools import ToolSession

PROPOSED_RESOURCE_CAP = 128
ROWS = [{"category": "Alpha", "amount": 7}, {"category": "Beta", "amount": 11}]
SPEC = {"kind": "bar", "x": "category", "y": "amount"}
ARGS = {"data": ROWS, "spec": SPEC}
SOURCE = Path(__file__).resolve().parents[1] / "src"


def sdk_metadata(result) -> dict:
    blocks = result[0] if isinstance(result, tuple) else result
    return json.loads(next(block.text for block in blocks if block.type == "text"))


def files(root: Path) -> dict[str, str]:
    return {str(path.relative_to(root)): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in root.rglob("*") if path.is_file()}


def assert_manifest(content: str) -> None:
    assert json.loads(content)["charts"][0]["records"] == ROWS


def test_r11_actual_sdk_resource_capacity_preflights_without_deleting_earliest(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    pytest.importorskip("mcp")
    from mcp.server.fastmcp.exceptions import ToolError

    output = tmp_path / "output"
    output.mkdir()
    host = output / "host-owned.txt"
    host.write_text("preserve caller file", encoding="utf-8")

    async def exercise() -> None:
        server = create_server(output)
        first_uri = None
        for _ in range(PROPOSED_RESOURCE_CAP // 2):
            info = sdk_metadata(await server.call_tool("render_echarts", ARGS))
            assert len(info["resources"]) == 2
            if first_uri is None:
                first_uri = next(r["uri"] for r in info["resources"] if r["mime_type"] == "application/json")
        before = files(output)
        assert len(await server.list_resources()) == PROPOSED_RESOURCE_CAP
        assert first_uri is not None
        earliest = list(await server.read_resource(first_uri))[0].content
        assert_manifest(earliest)
        generation_calls = []
        actual_render = ToolSession.render_chart

        def observe_render(self, *args, **kwargs):
            generation_calls.append(True)
            return actual_render(self, *args, **kwargs)

        # Observation delegates to the real render; admission must stop before this call.
        monkeypatch.setattr(ToolSession, "render_chart", observe_render)
        try:
            result = await server.call_tool("render_echarts", ARGS)
        except (ValueError, ToolError) as error:
            rejected, error_text = True, str(error)
        else:
            rejected, error_text = False, ""
            assert len(sdk_metadata(result)["resources"]) == 2
        after = files(output)
        assert list(await server.read_resource(first_uri))[0].content == earliest
        assert host.read_text(encoding="utf-8") == "preserve caller file"
        # Non-render calls must remain useful when issuance is full.
        profile = sdk_metadata(await server.call_tool("normalize_data", {"data": ROWS}))
        assert profile["input_count"] == len(ROWS)
        count = len(await server.list_resources())
        observation = {"proposed_cap": PROPOSED_RESOURCE_CAP, "registered_after": count,
                       "overcap_rejected": rejected, "files_before": len(before), "files_after": len(after),
                       "generation_calls_after_full": len(generation_calls),
                       "earliest_readable_unchanged": True, "host_file_preserved": True,
                       "normalization_recovery": True}
        (tmp_path / "observed.json").write_text(json.dumps(observation, indent=2), encoding="utf-8")
        assert rejected, f"Real SDK issued resources beyond proposed lifetime cap: {observation}"
        assert any(word in error_text.lower() for word in ("resource", "capacity", "budget", "limit"))
        assert len(error_text.encode("utf-8")) < 2048
        assert count == PROPOSED_RESOURCE_CAP and after == before and not generation_calls

    asyncio.run(exercise())


def test_r11_actual_sdk_capacity_reservation_is_atomic_for_concurrent_peers(tmp_path: Path) -> None:
    pytest.importorskip("mcp")
    from mcp.server.fastmcp.exceptions import ToolError

    async def exercise() -> None:
        server = create_server(tmp_path / "output")
        for _ in range(PROPOSED_RESOURCE_CAP // 2 - 2):
            sdk_metadata(await server.call_tool("render_echarts", ARGS))
        before = files(tmp_path / "output")
        # A schema-valid failed render must not consume a permanent reservation.
        with pytest.raises((ValueError, ToolError), match="data_dir"):
            await server.call_tool("render_echarts", {"data": {"file": "not-authorized.json"}, "spec": SPEC})
        assert files(tmp_path / "output") == before
        results = await asyncio.gather(*[server.call_tool("render_echarts", ARGS) for _ in range(4)],
                                       return_exceptions=True)
        successful = [result for result in results if not isinstance(result, BaseException)]
        errors = [result for result in results if isinstance(result, BaseException)]
        for result in successful:
            info = sdk_metadata(result)
            for resource in info["resources"]:
                if resource["mime_type"] == "application/json":
                    assert_manifest(list(await server.read_resource(resource["uri"]))[0].content)
        after = files(tmp_path / "output")
        count = len(await server.list_resources())
        assert all(after[path] == digest for path, digest in before.items())
        observation = {"proposed_cap": PROPOSED_RESOURCE_CAP, "peer_requests": 4,
                       "successful": len(successful), "errors": len(errors), "registered": count,
                       "prior_files_preserved": True, "schema_valid_failure_did_not_allocate": True}
        (tmp_path / "observed.json").write_text(json.dumps(observation, indent=2), encoding="utf-8")
        assert len(successful) == 2 and len(errors) == 2, f"Non-atomic/absent issuance admission: {observation}"
        assert all(isinstance(error, (ValueError, ToolError)) for error in errors)
        assert count == PROPOSED_RESOURCE_CAP and len(after) == len(before) + 4

    asyncio.run(exercise())


def test_r11_real_stdio_resource_capacity_list_read_and_error_recovery(tmp_path: Path) -> None:
    pytest.importorskip("mcp")
    from mcp import ClientSession, StdioServerParameters, types
    from mcp.client.stdio import stdio_client
    from mcp.shared.exceptions import McpError
    from pydantic import AnyUrl

    async def exercise() -> None:
        output = tmp_path / "output"
        output.mkdir()
        sentinel = output / "host-owned.txt"
        sentinel.write_text("preserve caller file", encoding="utf-8")
        params = StdioServerParameters(
            command=sys.executable, args=["-m", "deepviz.mcp_server", "--output-dir", str(output)],
            cwd=str(tmp_path),
            env={"PYTHONPATH": str(SOURCE), "PYTHONUTF8": "1", "PYTHONDONTWRITEBYTECODE": "1"},
        )
        with (tmp_path / "server.stderr").open("w", encoding="utf-8") as stderr:
            async with stdio_client(params, errlog=stderr) as (read, write):
                async with ClientSession(read, write, read_timeout_seconds=timedelta(seconds=60)) as session:
                    await session.initialize()
                    first_uri = None
                    for _ in range(PROPOSED_RESOURCE_CAP // 2):
                        result = await session.call_tool("render_echarts", ARGS)
                        assert not result.isError
                        info = sdk_metadata(result.content)
                        if first_uri is None:
                            first_uri = next(r["uri"] for r in info["resources"]
                                             if r["mime_type"] == "application/json")
                    assert len((await session.list_resources()).resources) == PROPOSED_RESOURCE_CAP
                    before = files(output)
                    bad = await session.call_tool("render_echarts", ARGS)
                    after = files(output)
                    count = len((await session.list_resources()).resources)
                    assert first_uri is not None
                    content = (await session.read_resource(first_uri)).contents[0]
                    assert isinstance(content, types.TextResourceContents)
                    assert_manifest(content.text)
                    with pytest.raises(McpError):
                        await session.read_resource(AnyUrl(sentinel.as_uri()))
                    valid = await session.call_tool("normalize_data", {"data": ROWS})
                    assert not valid.isError
                    assert sdk_metadata(valid.content)["input_count"] == len(ROWS)
                    assert len((await session.list_tools()).tools) == 7
                    assert sentinel.read_text(encoding="utf-8") == "preserve caller file"
                    observation = {"proposed_cap": PROPOSED_RESOURCE_CAP, "registered_after": count,
                                   "overcap_is_error": bad.isError, "files_before": len(before),
                                   "files_after": len(after), "earliest_resource_read": True,
                                   "unissued_file_uri_rejected": True, "normalize_and_discovery_recovery": True}
                    (tmp_path / "observed.json").write_text(json.dumps(observation, indent=2), encoding="utf-8")
                    assert bad.isError, f"Real stdio capacity policy absent: {observation}"
                    assert count == PROPOSED_RESOURCE_CAP and after == before
                    error = "\n".join(block.text for block in bad.content if block.type == "text")
                    assert len(error.encode("utf-8")) < 2048

    asyncio.run(asyncio.wait_for(exercise(), timeout=180))
