"""Independent SUM fixtures: literal binary64 inputs, fixed output memberships.

The oracle is Python's exact Fraction summation and float round-to-nearest-even,
not a translation of either candidate accumulator. No mean cases are added.
"""
from __future__ import annotations

import struct
from dataclasses import dataclass
from fractions import Fraction
from typing import TypedDict

MAX = "0x1.fffffffffffffp+1023"
NEG_MAX = "-0x1.fffffffffffffp+1023"
TINY = "0x0.0000000000001p-1022"
PROMOTE = (MAX, MAX, NEG_MAX, NEG_MAX)


@dataclass(frozen=True)
class SumCase:
    name: str
    rows: tuple[tuple[str, str | None], ...]
    # Explicit memberships avoid copying the candidate grouping/eviction logic.
    memberships: tuple[tuple[str, tuple[str, ...]], ...] = (("only", ("only",)),)
    max_points: int = 1000
    expects_other_warning: bool = False


def _single(name: str, values: tuple[str, ...]) -> SumCase:
    return SumCase(name, tuple(("only", value) for value in values))


def cases() -> tuple[SumCase, ...]:
    results = [
        _single("positive-promotion-binary-residual", PROMOTE + ("0x1.cp-3",)),
        _single("negative-promotion-binary-residual", (NEG_MAX, NEG_MAX, MAX, MAX, "-0x1.6p-4")),
        _single("prepromotion-compensation", (MAX, "0x1.4p-3", MAX, NEG_MAX, NEG_MAX)),
        _single("odd-mantissa-halfway-at-two", PROMOTE + ("0x1.0000000000001p+1", "0x1p-52")),
        _single("below-odd-mantissa-halfway", PROMOTE + ("0x1.0000000000001p+1", "0x1p-52", "-" + TINY)),
        _single("above-odd-mantissa-halfway", PROMOTE + ("0x1.0000000000001p+1", "0x1p-52", TINY)),
        _single("negative-odd-mantissa-halfway", PROMOTE + ("-0x1.0000000000001p+1", "-0x1p-52")),
        _single("halfway-below-one", PROMOTE + ("0x1.fffffffffffffp-1", "0x1p-54")),
        _single("negative-two-subnormal-units", PROMOTE + ("-0x1p-1022", "0x0.ffffffffffffep-1022")),
        _single("maximum-reconstructed", (MAX, MAX, NEG_MAX)),
        _single("late-promotion-after-prefix", ("0x0p+0",) * 37 + PROMOTE + ("0x1.ap-1",)),
        _single("ordinary-fastpath-compensated-control", ("0x1p+54", "0x1.4p-1", "-0x1p+54")),
        _single("positive-truly-unrepresentable", (MAX, MAX)),
        _single("negative-truly-unrepresentable", (NEG_MAX, NEG_MAX)),
    ]
    interleaved: list[tuple[str, str | None]] = []
    a = PROMOTE + ("0x1.9p-2",)
    b = (NEG_MAX, NEG_MAX, MAX, MAX, "-0x1.3p-3")
    for left, right in zip(a, b, strict=True):
        interleaved.extend((("a", left), ("b", right)))
    interleaved.extend((("empty", None), ("ordinary", "0x1.2p+2")))
    results.append(SumCase("interleaved-independent-groups", tuple(interleaved), (
        ("a", ("a",)), ("b", ("b",)), ("empty", ("empty",)), ("ordinary", ("ordinary",)),
    )))
    for promoted_before_eviction in (True, False):
        retained = tuple(("__deepviz_other__" if i == 0 else f"keep{i}", f"0x1p+{i}") for i in range(9))
        tail = (
            (("evicted", MAX), ("evicted", MAX), ("evicted", "0x1.5p-2"), ("incoming", NEG_MAX), ("incoming", NEG_MAX))
            if promoted_before_eviction else
            (("evicted", "0x1.5p-2"), ("incoming", MAX), ("incoming", MAX), ("incoming", NEG_MAX), ("incoming", NEG_MAX))
        )
        results.append(SumCase(
            "other-state-promoted-" + ("before-eviction" if promoted_before_eviction else "after-eviction"),
            retained + tail + (("keep3", "0x1.8p-1"),),
            tuple((group, (group,)) for group, _ in retained) + (("__deepviz_other___", ("evicted", "incoming")),),
            max_points=10, expects_other_warning=True,
        ))
    return tuple(results)


class Row(TypedDict):
    g: str
    v: float | None


def rows(case: SumCase) -> list[Row]:
    return [{"g": group, "v": None if value is None else float.fromhex(value)} for group, value in case.rows]


def bits(value: float | int | None) -> str | None:
    return None if value is None else struct.pack(">d", float(value)).hex()


def expected(case: SumCase) -> tuple[list[dict[str, str | float | None]], list[str | None], bool]:
    records: list[dict[str, str | float | None]] = []
    encoded: list[str | None] = []
    overflow = False
    for label, members in case.memberships:
        terms = [Fraction.from_float(float.fromhex(value)) for group, value in case.rows if group in members and value is not None]
        try:
            value = float(sum(terms, Fraction())) if terms else None
        except OverflowError:
            value = None
            overflow = True
        records.append({"g": label, "v": value})
        encoded.append(bits(value))
    return records, encoded, overflow
