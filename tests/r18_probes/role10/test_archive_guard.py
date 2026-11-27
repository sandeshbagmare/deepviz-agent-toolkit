"""Own extraction-harness guard tests, not product/browser acceptance totals."""
from __future__ import annotations

import tarfile

import pytest
from run_consumer import validate_members


def member(name: str, *, kind: bytes = tarfile.REGTYPE, size: int = 1) -> tarfile.TarInfo:
    result = tarfile.TarInfo(name)
    result.type = kind
    result.size = size
    return result


@pytest.mark.parametrize("name", ["../package/secret", "/package/absolute", "package/../secret",
                                 "package/C:/secret", "package\\secret", "package/src/source.ts",
                                 "package/node_modules/dependency.js", "package/.env"])
def test_own_archive_guard_rejects_unsafe_or_unreleased_members(name: str) -> None:
    with pytest.raises(AssertionError):
        validate_members([member(name)])


@pytest.mark.parametrize("kind", [tarfile.SYMTYPE, tarfile.LNKTYPE, tarfile.CHRTYPE, tarfile.FIFOTYPE])
def test_own_archive_guard_rejects_links_and_devices(kind: bytes) -> None:
    with pytest.raises(AssertionError):
        validate_members([member("package/dist/unsafe", kind=kind)])


def test_own_archive_guard_rejects_duplicates_or_oversized_members() -> None:
    with pytest.raises(AssertionError, match="Duplicate"):
        validate_members([member("package/dist/index.js"), member("package/dist/index.js")])
    with pytest.raises(AssertionError):
        validate_members([member("package/dist/large", size=2_000_001)])


def test_own_archive_guard_accepts_fixed_nested_raw_prompt_and_declaration_members() -> None:
    validate_members([member("package/dist/prompts/v1/system.md"), member("package/dist/index.d.ts")])
