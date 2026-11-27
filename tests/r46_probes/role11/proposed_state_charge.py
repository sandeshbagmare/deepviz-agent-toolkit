"""UNAPPLIED accounting proposal; never imported by production DeepViz."""
from typing import Any


def _state_number_bytes(value: Any) -> int:
    """Bound private numeric repr bytes without decimalizing wide integers."""
    if type(value) is int:
        bits: int = value.bit_length()
        # 30103 / 100000 > log10(2); include zero and a possible minus sign.
        return max(1, (bits * 30103 + 99999) // 100000) + int(value < 0)
    return len(repr(value))
