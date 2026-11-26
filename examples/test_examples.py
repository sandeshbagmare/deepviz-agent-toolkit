"""Explicit example checks: python -m pytest examples/test_examples.py."""
from __future__ import annotations

import asyncio
import json
import re
import subprocess
import sys
from pathlib import Path

from mcp_client import run


def test_mcp_download_keeps_static_preview_sibling_links(tmp_path: Path) -> None:
    """Renaming chart.svg without updating chart.html breaks an offline preview."""
    paths = [Path(value) for value in asyncio.run(run(tmp_path))]
    preview = next(path for path in paths if "matplotlib" in str(path) and path.suffix == ".html")
    image = re.search(r'<img[^>]+src="([^"]+)"', preview.read_text(encoding="utf-8"))
    assert image is not None
    assert (preview.parent / image.group(1)).is_file(), "downloaded HTML must resolve its SVG sibling"


def test_local_deep_agent_executes_the_three_tool_chain(tmp_path: Path) -> None:
    result = subprocess.run(
        [sys.executable, str(Path(__file__).with_name("deep_agent_local.py")),
         "--output-dir", str(tmp_path)],
        capture_output=True, text=True, check=False,
    )
    assert result.returncode == 0, result.stderr
    output = json.loads(result.stdout)
    assert output["mode"] == "deterministic-local-model"
    assert output["tools_called"] == ["normalize_data", "recommend_chart", "render_matplotlib"]
    assert output["artifact"]["input_count"] == 3
    assert output["artifact"]["output_count"] == 3
    assert any(Path(path).is_file() for path in output["artifact"]["paths"] if path.endswith(".png"))
