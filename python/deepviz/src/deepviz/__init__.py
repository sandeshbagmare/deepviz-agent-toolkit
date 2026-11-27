"""Schema-driven visualization; agent and MCP dependencies are optional."""
from __future__ import annotations

from importlib.resources import files
from pathlib import Path
from typing import Any

from .models import Artifact, ChartSpec, NormalizedData
from .normalize import normalize
from .render import render

__all__ = ["Artifact", "ChartSpec", "NormalizedData", "create_tools", "normalize", "read_prompt", "render"]
__version__ = "0.1.0"


def read_prompt(name: str = "system", *, version: int = 1) -> str:
    """Read a versioned policy/request from installed package resources."""
    if name not in {"system", "request"} or version != 1:
        raise ValueError("Available prompts are 'system' and 'request', version=1")
    return files("deepviz").joinpath(f"resources/prompts/v1/{name}.md").read_text(encoding="utf-8")


def create_tools(output_dir: str | Path | None = None, *, data_dir: str | Path | None = None) -> list[Any]:
    """Create five StructuredTool renderers plus profile and recommendation tools."""
    from .tools import create_tools as make_tools

    return make_tools(output_dir, data_dir=data_dir)
