from __future__ import annotations

import json
import struct
from fractions import Fraction
from pathlib import Path


def bits(value: float) -> str:
    return struct.pack('>d', value).hex()


def main() -> None:
    tiny = float.fromhex('0x0.0000000000001p-1022')
    maximum = float.fromhex('0x1.fffffffffffffp+1023')
    next_one = float.fromhex('0x1.0000000000001p+0')
    next_two = float.fromhex('0x1.0000000000002p+0')
    cases: list[tuple[str, list[object]]] = [
        ('positive-four-thirds-subnormal', [tiny, tiny, 2 * tiny]),
        ('negative-four-thirds-subnormal', [-tiny, -tiny, -2 * tiny]),
        ('positive-third-underflow', [tiny, 0.0, 0.0]),
        ('negative-third-underflow', [-tiny, 0.0, 0.0]),
        ('normal-even-tie-down', [1.0, next_one]),
        ('normal-odd-tie-up', [next_one, next_two]),
        ('maximum-finite-constant', [maximum, maximum]),
        ('maximum-finite-signed-third', [maximum, maximum, -maximum]),
        ('opposite-maximum-plus-tiny', [maximum, -maximum, tiny]),
        ('wide-cancellation-half', [2.0 ** 1023, 1.0, -(2.0 ** 1023), 1.0]),
        ('cross-initialization-37', [*([tiny] * 32), maximum, maximum, -maximum, -maximum, 5 * tiny]),
        ('valid-denominator-only', [1.0, None, 3.0, False, '9']),
        ('all-nonnumeric', [None, False, '9']),
        ('weighted-tail-reference', [0.0, 0.0, 12.0, 12.0, 12.0, 12.0]),
    ]
    rows = []
    for label, values in cases:
        numeric = [Fraction.from_float(value) for value in values if type(value) is float]
        exact = sum(numeric, Fraction()) / len(numeric) if numeric else None
        expected = float(exact) if exact is not None else None
        rows.append({'label': label, 'values': values, 'valid_count': len(numeric),
                     'input_bits': [bits(value) if type(value) is float else None for value in values],
                     'expected': expected, 'expected_bits': bits(expected) if expected is not None else None,
                     'exact_numerator': str(exact.numerator) if exact is not None else None,
                     'exact_denominator': str(exact.denominator) if exact is not None else None})
    output = Path('artifacts/r39-15/reference-vectors.json')
    assert not output.exists()
    output.write_text(json.dumps({'oracle': 'stdlib Fraction.from_float exact rational, one float rounding; no deepviz imports',
                                 'vectors': rows}, indent=2, allow_nan=False) + '\n', encoding='utf-8', newline='\n')
    print('R39_INDEPENDENT_STDLIB_RATIONAL_REFERENCE14_CREATED_NO_PRODUCTION_IMPORT')


if __name__ == '__main__':
    main()