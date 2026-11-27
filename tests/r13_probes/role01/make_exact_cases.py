"""Generate small exact Fraction oracles, independent of either reducer."""
from __future__ import annotations

import json
import math
import random
from fractions import Fraction
from pathlib import Path


def cases() -> list[dict]:
    result = []

    def add(name: str, family: str, values: list[float]) -> None:
        exact = sum(map(Fraction, values), Fraction())
        result.append({"name": name, "family": family, "values": values, "expected": float(exact)})

    high = 1e308
    prefix = [high, high, -high, -high]
    for exponent in (-1021, -500, 0, 500, 1023):
        even = math.ldexp(1.0, exponent)
        for parity, center in (("even", even), ("odd", math.nextafter(even, math.inf))):
            for sign in (-1, 1):
                add(f"tie-{exponent}-{parity}-{sign}", "tie", prefix + [sign * center, sign * math.ldexp(1.0, exponent - 53)])
    rng = random.Random(131601)
    for index in range(32):
        tail = [math.ldexp(rng.randint(-1000, 1000) / 1024, rng.randint(-1074, 1000)) for _ in range(8)]
        add(f"post-promotion-exact-{index}", "exact", prefix + tail)
    for value in (0.125, math.ldexp(1.0, 970), -math.ldexp(1.0, 970)):
        add(f"carry-{value.hex()}", "carry", [high, value, high, -high, -high])
    for name, low in (("unit", 1.0), ("subnormal", math.ulp(0.0))):
        middle = 1e200 if name == "unit" else 1.0
        add(f"pre-promotion-{name}", "pre-promotion", [high, middle, low, -middle, high, -high, -high])
        add(f"same-multiset-promoted-first-{name}", "order-control", prefix + [middle, low, -middle])
    return result


if __name__ == "__main__":
    Path(__file__).with_name("exact-cases.json").write_text(
        json.dumps(cases(), indent=2, allow_nan=False) + "\n", encoding="utf-8", newline="\n",
    )