"""Independent P1 boundary controls; strict callback-order oracle is intentionally unchanged."""
from __future__ import annotations

import asyncio
import importlib
import json
import os
import sys
from pathlib import Path
from types import FrameType
from typing import Any

import pytest
from langchain_core.callbacks import BaseCallbackHandler
from mcp.server.fastmcp.utilities.func_metadata import FuncMetadata

from deepviz.mcp_server import create_server
from deepviz.tools import ToolSession, create_tools

ROWS = [{"label": "東京 📊", "value": 7}]


def save(name: str, value: Any) -> None:
    if directory := os.environ.get("R22_02_RESULTS"):
        with (Path(directory) / f"{name}.json").open("x", encoding="utf-8") as stream:
            json.dump(value, stream, indent=2, allow_nan=False)
            stream.write("\n")


@pytest.fixture(scope="session", autouse=True)
def pinned_imports() -> None:
    source = Path(os.environ["R22_02_SOURCE"]).resolve()
    for name in ("tools", "mcp_server", "normalize", "models"):
        module = importlib.import_module(f"deepviz.{name}")
        assert module.__file__ is not None
        assert Path(module.__file__).resolve() == source / "python/deepviz/src/deepviz" / f"{name}.py"


class CallbackSpy(BaseCallbackHandler):
    def __init__(self) -> None:
        self.starts: list[dict[str, Any]] = []

    def on_tool_start(self, serialized: dict[str, Any], input_str: str, **kwargs: Any) -> None:
        self.starts.append({"utf8_bytes": len(input_str.encode("utf-8")), "public_marker_seen": "PUBLIC_R22" in input_str})


def execute(tool: Any, method: str, value: Any, spy: CallbackSpy) -> Any:
    result = getattr(tool, method)(value, callbacks=[spy])
    return asyncio.run(result) if method == "arun" else result


def invalid_raw_cases() -> dict[str, str]:
    small = json.dumps([{"label": "PUBLIC_R22 東京 📊", "value": 7}], ensure_ascii=False)
    raw = " " * (1_000_001 - len(small.encode("utf-8"))) + small
    assert len(raw) < 1_000_000 < len(raw.encode("utf-8"))
    return {
        "escaped_duplicate": r'[{"label":"PUBLIC_R22","value":1,"\u0076alue":2}]',
        "unicode_raw_1000001_bytes": raw,
        "encoded_depth5000": "[" * 5000 + "]" * 5000,
    }


@pytest.mark.parametrize("method", ["run", "arun"])
@pytest.mark.parametrize("shape", ["bare", "data-dict"])
def test_all_supported_call_forms_admit_before_callback(method: str, shape: str, tmp_path: Path) -> None:
    tool = next(item for item in create_tools(tmp_path / "out") if item.name == "normalize_data")
    observations: list[dict[str, Any]] = []
    for name, raw in invalid_raw_cases().items():
        spy = CallbackSpy()
        with pytest.raises(ValueError) as rejected:
            execute(tool, method, {"data": raw} if shape == "data-dict" else raw, spy)
        assert len(str(rejected.value)) < 500
        observations.append({"case": name, "raw_utf8_bytes": len(raw.encode("utf-8")),
                             "raw_characters": len(raw), "rejected_type": type(rejected.value).__name__,
                             "error": str(rejected.value), "callback_starts": spy.starts})
    recovery_spy = CallbackSpy()
    recovered = execute(tool, method, {"data": ROWS} if shape == "data-dict" else json.dumps(ROWS, ensure_ascii=False), recovery_spy)
    assert recovered["input_count"] == 1 and len(recovery_spy.starts) == 1
    assert not (tmp_path / "out").exists()
    save(f"callback-order-{method}-{shape}", {"observations": observations, "ordinary_recovery_count": recovered["input_count"]})
    assert all(not row["callback_starts"] for row in observations), (
        f"Rejected {shape} input reached {method} callbacks before validation: "
        + ", ".join(row["case"] for row in observations if row["callback_starts"])
    )


@pytest.mark.parametrize("method", ["run", "arun"])
def test_bare_string_is_a_supported_public_form_with_exact_raw_limit(method: str, tmp_path: Path) -> None:
    tool = next(item for item in create_tools(tmp_path / "out") if item.name == "normalize_data")
    small = json.dumps(ROWS, ensure_ascii=False)
    raw = " " * (1_000_000 - len(small.encode("utf-8"))) + small
    spy = CallbackSpy()
    result = execute(tool, method, raw, spy)
    assert result["input_count"] == 1 and len(spy.starts) == 1
    assert not (tmp_path / "out").exists()
    save(f"bare-positive-{method}", {"raw_utf8_bytes": len(raw.encode("utf-8")), "input_count": 1,
                                      "callback_count": len(spy.starts), "scope": "Bare strings really work; not an invalid calling convention"})


def metadata(result: Any) -> dict[str, Any]:
    if isinstance(result, dict):
        return result
    if isinstance(result, tuple):
        return metadata(result[0])
    return json.loads(next(block.text for block in result if block.type == "text"))


def test_mcp_escaped_control_duplicates_and_raw_bytes_stop_before_sdk_preparse(tmp_path: Path) -> None:
    (tmp_path / "safe.json").write_text(json.dumps(ROWS), encoding="utf-8")
    server = create_server(tmp_path / "out", data_dir=tmp_path)
    preparse_calls = 0
    watched = FuncMetadata.pre_parse_json.__code__

    def observe(frame: FrameType, event: str, arg: Any) -> None:
        nonlocal preparse_calls
        if event == "call" and frame.f_code is watched:
            preparse_calls += 1

    previous = sys.getprofile()
    observations: list[dict[str, Any]] = []
    for name, raw in {**invalid_raw_cases(), "escaped_file_control": r'{"file":"../outside.json","\u0066ile":"safe.json"}'}.items():
        sys.setprofile(observe)
        try:
            with pytest.raises(ValueError) as rejected:
                asyncio.run(server.call_tool("normalize_data", {"data": raw}))
        finally:
            sys.setprofile(previous)
        assert len(str(rejected.value)) < 500
        observations.append({"case": name, "error": str(rejected.value), "sdk_preparse_calls": preparse_calls})
        assert preparse_calls == 0, "Invalid encoded input entered the SDK's permissive decoder"
    sys.setprofile(observe)
    try:
        valid = metadata(asyncio.run(server.call_tool("normalize_data", {"data": json.dumps(ROWS, ensure_ascii=False)})))
    finally:
        sys.setprofile(previous)
    assert valid["input_count"] == 1 and preparse_calls == 1
    assert not (tmp_path / "out").exists()
    save("mcp-admission-order", {"invalid": observations, "positive_sdk_preparse_calls": preparse_calls,
                                 "method": "Read-only sys.setprofile code-entry count; no patched method/cap/SDK; no frame retained"})


def test_escaped_file_and_handle_keys_are_canonical_but_never_cache_a_resolved_path(tmp_path: Path) -> None:
    root = tmp_path / "data"
    root.mkdir()
    safe = root / "safe.json"
    safe.write_text(json.dumps(ROWS), encoding="utf-8")
    outside = tmp_path / "outside.json"
    outside.write_text('[{"PUBLIC_OUTSIDE_R22":999}]', encoding="utf-8")
    sentinel = outside.read_bytes()
    session = ToolSession(tmp_path / "out", data_dir=root)
    first = session.normalize_data(r'{"\u0066ile":"safe\u002ejson"}')
    copied = session.normalize_data('{"dataset\\u005fid":' + json.dumps(first["dataset_id"]) + '}')
    sources = [session.datasets[value["dataset_id"]]["source"] for value in (first, copied)]
    assert sources == [{"file": "safe.json"}, {"file": "safe.json"}]
    assert all(isinstance(value, dict) and not isinstance(value, Path) for value in sources)
    with pytest.raises(ValueError, match="escapes"):
        session.normalize_data(r'{"file":"\u002e\u002e/outside.json"}')
    with pytest.raises(ValueError, match="no URLs"):
        session.normalize_data(r'{"file":"https\u003a//invalid.test/x"}')
    assert outside.read_bytes() == sentinel and len(session.datasets) == 2
    assert not (tmp_path / "out").exists()
    safe.write_text('[{"label":"changed-local","value":2},{"label":"second","value":3}]', encoding="utf-8")
    reread = session.normalize_data({"dataset_id": copied["dataset_id"]})
    assert reread["input_count"] == 2
    save("canonical-encoded-authority", {"canonical_sources": sources, "original_count": first["input_count"],
                                          "reread_count": reread["input_count"], "outside_sentinel_preserved": True,
                                          "invalid_references_cached": False, "artifacts_created": False})
