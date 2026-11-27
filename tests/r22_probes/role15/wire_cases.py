"""Literal numeric JSON wire oracle from the approved #30 contract, not source."""
from __future__ import annotations

from dataclasses import dataclass

# Deliberately explicit approved values; never obtained from model/schema fields.
NUMERIC_DEFAULTS = {"version": 1, "max_points": 2000, "width": 900, "height": 520, "columns": 2}
NUMERIC_CONTRACT = (
    ("version", 1, 1, "1.0", "1.5"),
    ("max_points", 10, 100000, "2000.0", "2000.5"),
    ("width", 240, 4096, "900.0", "900.5"),
    ("height", 200, 4096, "520.0", "520.5"),
    ("columns", 1, 6, "2.0", "2.5"),
)


@dataclass(frozen=True)
class WireCase:
    name: str
    wire: str
    accepted: bool
    expected_numeric_overrides: tuple[tuple[str, int], ...] = ()


def wire_cases() -> tuple[WireCase, ...]:
    result = [WireCase("omitted-defaults", "{}", True)]
    for key, minimum, maximum, integral, fractional in NUMERIC_CONTRACT:
        result.extend((
            WireCase(f"{key}-numeric-string", '{"' + key + '":"' + integral + '"}', False),
            WireCase(f"{key}-boolean-true", '{"' + key + '":true}', False),
            WireCase(f"{key}-boolean-false", '{"' + key + '":false}', False),
            WireCase(f"{key}-null", '{"' + key + '":null}', False),
            WireCase(f"{key}-nonintegral", '{"' + key + '":' + fractional + '}', False),
            WireCase(f"{key}-integral-json-float", '{"' + key + '":' + integral + '}', True),
            WireCase(f"{key}-lower-bound", '{"' + key + '":' + str(minimum) + '}', True, ((key, minimum),)),
            WireCase(f"{key}-below-bound", '{"' + key + '":' + str(minimum - 1) + '}', False),
            WireCase(f"{key}-above-bound", '{"' + key + '":' + str(maximum + 1) + '}', False),
        ))
        if minimum != maximum:
            result.append(WireCase(f"{key}-upper-bound", '{"' + key + '":' + str(maximum) + '}', True, ((key, maximum),)))
    result.extend((
        WireCase("integral-exponent-width", '{"width":9e2}', True),
        WireCase("integral-exponent-version", '{"version":1e0}', True),
        WireCase("finite-extreme-positive-outside-bound", '{"width":1e309}', False),
        WireCase("finite-extreme-negative-outside-bound", '{"height":-1e309}', False),
        WireCase("numeric-array-is-not-scalar", '{"width":[900]}', False),
        WireCase("numeric-object-is-not-scalar", '{"width":{"value":900}}', False),
        WireCase("unknown-kind", '{"kind":"executable"}', False),
        WireCase("literal-untrusted-title-is-data", '{"title":"<script>literal data only</script>"}', True),
        WireCase("child-integral-float", '{"kind":"dashboard","charts":[{"width":900.0}]}', True),
        WireCase("child-string-width", '{"kind":"dashboard","charts":[{"width":"900"}]}', False),
        WireCase("child-boolean-version", '{"kind":"dashboard","charts":[{"version":true}]}', False),
        WireCase("child-extra-expression", '{"kind":"dashboard","charts":[{"expression":"not executable"}]}', False),
    ))
    for key in ("code", "expression", "javascript", "sql", "url"):
        result.append(WireCase(f"extra-{key}", '{"' + key + '":"not executable"}', False))
    return tuple(result)


INVALID_JSON_WIRES = (
    ("NaN-token", '{"width":NaN}'),
    ("Infinity-token", '{"width":Infinity}'),
    ("negative-Infinity-token", '{"width":-Infinity}'),
)
