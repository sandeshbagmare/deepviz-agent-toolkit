"""DeepViz's staged data library; rendering, tools and CLI are not shipped yet."""
from __future__ import annotations

from importlib.resources import files

from .models import Artifact, ChartSpec, NormalizedData
from .normalize import normalize

__all__ = ["Artifact", "ChartSpec", "NormalizedData", "__version__", "normalize", "read_prompt"]
__version__ = "0.1.0"


def read_prompt(name: str = "system", *, version: int = 1) -> str:
    """Read a versioned policy/request from installed package resources."""
    if name not in {"system", "request"} or version != 1:
        raise ValueError("Available prompts are 'system' and 'request', version=1")
    return files("deepviz").joinpath(f"resources/prompts/v1/{name}.md").read_text(encoding="utf-8")
