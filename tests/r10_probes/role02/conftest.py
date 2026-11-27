"""Require these independent probes to exercise their own source checkout."""
from __future__ import annotations

import importlib
from pathlib import Path

import pytest


@pytest.fixture(scope="session", autouse=True)
def require_own_source_checkout() -> None:
    """Do not mistake the shared venv editable MAIN installation for the pin."""
    root = Path(__file__).resolve().parents[3]
    source = root / "python" / "deepviz" / "src" / "deepviz"
    for name in ("models", "normalize", "tools", "mcp_server", "engines", "render"):
        module = importlib.import_module(f"deepviz.{name}")
        filename = module.__file__
        assert filename is not None, name
        assert Path(filename).resolve() == source / f"{name}.py", name
