"""Complete actual positive lifetime checks with homogeneous bounded literals.

The first mixed-type diagnostic fails BEFORE its closure assertions. Keep that
diagnostic unchanged; these additional cases test the previously-unreached work.
"""
from __future__ import annotations

import io
from pathlib import Path
from typing import Any

import pytest

from deepviz import normalize


@pytest.mark.parametrize("owned", [False, True], ids=["borrowed-stays-open", "owned-closes-and-renames"])
def test_real_positive_jsonl_ownership(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, owned: bool) -> None:
    text = '{"v":0}\n{"v":-2}\n{"v":3}\n'
    path = tmp_path / "homogeneous-positive.jsonl"
    path.write_text(text, encoding="utf-8")
    seen: list[Any] = []
    original_open = Path.open

    def observed(self: Path, *args: Any, **kwargs: Any) -> Any:
        file = original_open(self, *args, **kwargs)
        if self == path:
            seen.append(file)
        return file

    monkeypatch.setattr(Path, "open", observed)
    borrowed = io.StringIO(text)
    try:
        result = normalize(path if owned else borrowed, {"kind": "table", "format": "jsonl", "aggregation": "none"})
        assert result.records == [{"v": 0}, {"v": -2}, {"v": 3}]
        assert (result.input_count, result.strategy, result.warnings) == (3, "none", [])
        if owned:
            assert seen and all(file.closed for file in seen)
            moved = path.with_suffix(".released")
            path.rename(moved)
            assert moved.read_text(encoding="utf-8") == text
        else:
            assert not borrowed.closed
            borrowed.seek(0)
            assert borrowed.read() == text
    finally:
        borrowed.close()
