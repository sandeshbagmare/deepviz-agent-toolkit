"""Stream heterogeneous inputs into bounded, JSON-safe chart records.

Scalar sequences become ``index``/``value`` records. Nested object keys and
array indices are dotted. Strings are content; only ``Path`` opts into files.
JSONL, delimited files, generators and Arrow batches stream; an already encoded
JSON document is decoded as a whole by the standard library.

``auto`` sums numeric measures for categorical charts (or counts rows when no
measure is available); other charts use deterministic reservoir sampling once
``max_points`` is exceeded. ``none`` also samples with a warning at that limit:
the bounded output contract takes precedence over unbounded identity output.
Explicit reductions group by x and color, or reduce globally without a category.
Sums/means retain a bounded compensation term for floating-point cancellation.
Heatmaps instead group by both x/y coordinates and reduce the color measure;
without color, automatic heatmap aggregation counts rows into a ``count`` field.
Count includes every row and writes the mapped measure field, or ``count``
when that measure is omitted.
Other reducers ignore null/non-numeric measures; an
all-null group yields None. High cardinality retains the first max_points - 1
groups and merges *all* remaining contributions into a warned other bucket.
The other mean is weighted by valid raw observations, never by group means.
The bucket label is ``__deepviz_other__``, with underscores appended if needed
to distinguish it from retained category labels.
Reservoir samples retain original source order, but are not temporal/extrema-aware
and may miss peaks and short-lived events.
"""
from __future__ import annotations

import csv
import io
import json
import math
import random
import re
from collections import Counter
from collections.abc import Generator, Iterable, Iterator, Mapping
from datetime import date, datetime, time
from decimal import Decimal
from itertools import chain, islice, zip_longest
from numbers import Integral, Real
from pathlib import Path
from typing import Any

from .models import ChartSpec, NormalizedData

_MAX_FIELDS = 1024
_MAX_DEPTH = 64
_MAX_CELL_BYTES = 64 * 1024
_MAX_FIELD_BYTES = 4 * 1024
_MAX_RECORD_BYTES = 256 * 1024
_MAX_RETAINED_BYTES = 16 * 1024 * 1024
_BATCH_SIZE = 4096
_REDUCTIONS = {"sum", "mean", "count", "min", "max"}
_CATEGORICAL = {"bar", "pie", "radar", "treemap", "sunburst", "funnel"}
_METADATA = {"pageInfo", "totalCount", "count", "extensions", "errors", "meta", "pagination"}
_WRAPPERS = ("data", "records", "rows", "items", "results")
_PATH_FORMATS = {
    ".csv": "csv", ".tsv": "tsv", ".jsonl": "jsonl", ".ndjson": "jsonl",
    ".parquet": "parquet", ".arrow": "arrow", ".feather": "arrow", ".ipc": "arrow",
}
_NUMBER = re.compile(r"-?(?:0|[1-9]\d*)(?:\.\d+)?(?:[eE][+-]?\d+)?\Z")
_JSON_ESCAPE = re.compile(r'["\\\x00-\x1f]')
_ABSENT = object()
_PRIMITIVES = (str, int, bool, float, type(None))


def _iterable(value: Any) -> bool:
    if type(value) in _PRIMITIVES:
        return False
    return isinstance(value, Iterable) and not isinstance(value, (str, bytes, bytearray, Mapping))


def _json(text: str, location: str = "content") -> Any:
    try:
        return json.loads(text, object_pairs_hook=_unique_json_object)
    except (ValueError, RecursionError) as error:
        raise ValueError(f"Invalid JSON {location}: {error}") from error


def _unique_json_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    record: dict[str, Any] = {}
    for key, value in pairs:
        if key in record:
            raise ValueError("Duplicate JSON object key")
        record[key] = value
    return record


def _without_bom(lines: Iterable[str]) -> Iterator[str]:
    iterator = iter(lines)
    first = next(iterator, None)
    if first is not None:
        yield first.removeprefix("\ufeff")
    # Delegation would forward close() to a caller-owned stream on parser failure.
    for line in iterator:  # noqa: UP028 - must not forward close() to borrowed input
        yield line


def _jsonl(lines: Iterable[str]) -> Iterator[Any]:
    for number, line in enumerate(_without_bom(lines), 1):
        if line.strip():
            yield _json(line, f"at line {number}")


def _cell(value: str) -> Any:
    stripped = value.strip()
    if not stripped:
        return None
    if _NUMBER.fullmatch(stripped):
        return float(stripped) if any(char in stripped for char in ".eE") else int(stripped)
    if stripped.lower() in {"nan", "inf", "+inf", "-inf", "infinity", "+infinity", "-infinity"}:
        return float(stripped)
    return value


def _delimited(lines: Iterable[str], delimiter: str) -> Iterator[dict[str, Any]]:
    reader = csv.reader(_without_bom(lines), delimiter=delimiter, strict=True)
    try:
        header = next(reader, None)
        if header is None:
            return
        if any(not name.strip() for name in header):
            raise ValueError("Delimited content has an empty column name")
        if len(set(header)) != len(header):
            raise ValueError("Delimited content has duplicate column names")
        if len(header) > _MAX_FIELDS:
            raise ValueError(f"Input exceeds {_MAX_FIELDS} fields")
        for values in reader:
            if not values:
                continue
            if len(values) != len(header):
                raise ValueError(f"Wrong column count at line {reader.line_num}")
            yield dict(zip(header, map(_cell, values), strict=True))
    except csv.Error as error:
        raise ValueError(f"Invalid delimited content at line {reader.line_num}: {error}") from error


def _text(text: str, format: str) -> Any:
    text = text.lstrip("\ufeff")
    if format == "jsonl":
        return _jsonl(io.StringIO(text))
    if format in {"csv", "tsv"}:
        return _delimited(io.StringIO(text), "\t" if format == "tsv" else ",")
    if format == "json":
        return _json(text)
    if format != "auto":
        raise ValueError(f"Format {format!r} requires binary content or a Path")
    if not text.strip():
        return iter(())
    try:
        return json.loads(text, object_pairs_hook=_unique_json_object)
    except json.JSONDecodeError as error:
        if error.msg == "Extra data" and text.lstrip().startswith(("{", "[")):
            return _jsonl(io.StringIO(text))
        first = text.split("\n", 1)[0]
        if not text.lstrip().startswith(("{", "[")) and ("," in first or "\t" in first):
            return _delimited(io.StringIO(text), "\t" if "\t" in first else ",")
        raise ValueError("Content is not valid JSON, JSONL or delimited content; specify format") from error
    except RecursionError as error:
        raise ValueError("JSON content is nested too deeply") from error


def _arrow_module() -> Any:
    try:
        import pyarrow
    except ImportError as error:
        raise ImportError("Arrow/Parquet ingestion requires deepviz-agent-toolkit[columnar]") from error
    return pyarrow


def _arrow_rows(data: Any) -> Iterator[dict[str, Any]]:
    arrow = _arrow_module()
    if isinstance(data, arrow.Table):
        batches = data.to_reader(max_chunksize=_BATCH_SIZE)
    elif isinstance(data, arrow.RecordBatch):
        batches = (data,)
    elif isinstance(data, arrow.RecordBatchReader):
        batches = data
    else:
        raise TypeError("Unsupported Arrow input; expected Table, RecordBatch or RecordBatchReader")
    _validate_arrow_fields(data.schema)
    for batch in batches:
        for offset in range(0, batch.num_rows, _BATCH_SIZE):
            yield from batch.slice(offset, _BATCH_SIZE).to_pylist()


def _validate_arrow_fields(fields: Iterable[Any], depth: int = 0) -> None:
    if depth > _MAX_DEPTH:
        raise ValueError("Arrow schema is nested too deeply")
    names = set()
    for index, field in enumerate(fields):
        if index >= _MAX_FIELDS:
            raise ValueError(f"Arrow schema exceeds {_MAX_FIELDS} fields")
        if field.name in names:
            raise ValueError("Duplicate Arrow schema field name")
        names.add(field.name)
        _utf8_size(field.name, _MAX_FIELD_BYTES, "field name")
        dtype = getattr(field.type, "storage_type", field.type)
        if not dtype.num_fields and hasattr(dtype, "value_type"):
            dtype = dtype.value_type
        _validate_arrow_fields((dtype.field(i) for i in range(dtype.num_fields)), depth + 1)


def _binary_rows(data: Any, format: str) -> Iterator[dict[str, Any]]:
    arrow = _arrow_module()
    source = str(data) if isinstance(data, Path) else arrow.BufferReader(data)
    if format == "parquet":
        import pyarrow.parquet as parquet

        with parquet.ParquetFile(source) as file:
            _validate_arrow_fields(file.schema_arrow)
            for batch in file.iter_batches(batch_size=_BATCH_SIZE):
                yield from batch.to_pylist()
        return
    # IPC file and IPC stream are separate Arrow encodings; both stay batch bounded.
    with arrow.input_stream(source) if isinstance(source, str) else source as stream:
        try:
            reader = arrow.ipc.open_file(stream)
        except arrow.ArrowInvalid:
            stream.seek(0)
            yield from _arrow_rows(arrow.ipc.open_stream(stream))
        else:
            _validate_arrow_fields(reader.schema)
            for index in range(reader.num_record_batches):
                yield from _arrow_rows(reader.get_batch(index))


def _path_rows(path: Path, format: str) -> Iterator[Any]:
    if format in {"arrow", "parquet"}:
        yield from _binary_rows(path, format)
        return
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        if format == "jsonl":
            yield from _jsonl(stream)
        else:
            yield from _delimited(stream, "\t" if format == "tsv" else ",")


def _source(data: Any, format: str) -> Any:
    if isinstance(data, Path):
        if format == "auto":
            format = _PATH_FORMATS.get(data.suffix.lower(), "auto")
        if format in {"auto", "json"}:
            with data.open("r", encoding="utf-8-sig") as stream:
                return _text(stream.read(), format)
        return _path_rows(data, format)
    if type(data).__module__.split(".", 1)[0] == "pyarrow":
        return _arrow_rows(data)
    if isinstance(data, (bytes, bytearray, memoryview)):
        if format in {"arrow", "parquet"}:
            return _binary_rows(data, format)
        try:
            data = bytes(data).decode("utf-8-sig")
        except UnicodeDecodeError as error:
            raise ValueError("Content must be UTF-8, or specify an Arrow/Parquet format") from error
    if isinstance(data, str):
        return _text(data, format)
    if isinstance(data, io.TextIOBase):
        if format == "jsonl":
            return _jsonl(data)
        if format in {"csv", "tsv"}:
            return _delimited(data, "\t" if format == "tsv" else ",")
        return _text(data.read(), format)
    return data


def _select_path(value: Any, tokens: list[str], counts: Counter[str], depth: int = 0) -> Iterator[Any]:
    if depth > _MAX_DEPTH:
        raise ValueError("data_path is nested too deeply")
    if not tokens:
        counts["path_matches"] += 1
        if value is None:
            counts["null_nodes"] += 1
        else:
            yield value
    elif isinstance(value, Mapping):
        _graphql_errors(value, counts)
        if tokens[0] in value:
            yield from _select_path(value[tokens[0]], tokens[1:], counts, depth + 1)
        else:
            counts["path_missing"] += 1
    elif _iterable(value):
        if tokens[0].isdecimal():
            selected = next(islice(iter(value), int(tokens[0]), None), _ABSENT)
            if selected is _ABSENT:
                counts["path_missing"] += 1
            else:
                yield from _select_path(selected, tokens[1:], counts, depth + 1)
        else:
            had_items = False
            for item in value:
                had_items = True
                yield from _select_path(item, tokens, counts, depth + 1)
            if not had_items:
                counts["path_empty"] += 1
    else:
        counts["path_missing"] += 1


def _connection(value: Mapping[str, Any], depth: int = 0) -> Mapping[str, Any] | None:
    if depth > _MAX_DEPTH:
        raise ValueError("GraphQL response is nested too deeply")
    if "edges" in value or "nodes" in value:
        if "edges" in value and "nodes" in value:
            raise ValueError("GraphQL connection has both edges and nodes; select one with data_path")
        if set(value).difference({"edges", "nodes"}, _METADATA):
            raise ValueError("Ambiguous GraphQL connection fields; select rows with data_path")
        return value
    children = [child for key, child in value.items() if key not in _METADATA]
    if len(children) == 1 and isinstance(children[0], Mapping):
        return _connection(children[0], depth + 1)
    if len(children) > 1 and any(
        _connection(child, depth + 1) is not None for child in children if isinstance(child, Mapping)
    ):
        raise ValueError("Multiple/ambiguous GraphQL fields require an explicit data_path")
    return None


def _graphql_errors(value: Mapping[str, Any], counts: Counter[str]) -> None:
    if value.get("errors") and ("data" in value or set(value).issubset(_METADATA)):
        if not value.get("data"):
            raise ValueError("GraphQL response contains errors and no data")
        counts["graphql_errors"] += 1


def _expand(value: Any, counts: Counter[str], depth: int = 0, record: bool = False) -> Iterator[Any]:
    if depth > _MAX_DEPTH:
        raise ValueError("Input is nested too deeply or cyclic")
    if isinstance(value, dict) or isinstance(value, Mapping):
        if not value:
            if depth:
                yield value
            return
        if len(value) > _MAX_FIELDS:
            raise ValueError(f"Input exceeds {_MAX_FIELDS} fields")
        _graphql_errors(value, counts)
        if "node" in value and set(value).issubset({"node", "cursor"}):
            if value["node"] is None:
                counts["null_nodes"] += 1
            else:
                yield from _expand(value["node"], counts, depth + 1, record=True)
            return
        protocol = "data" in value or "edges" in value or "nodes" in value
        nested_wrapper = not record and all(isinstance(child, Mapping) for child in value.values())
        connection = _connection(value) if protocol or nested_wrapper else None
        if connection is not None:
            if not protocol and not any(wrapper in value for wrapper in _WRAPPERS):
                raise ValueError("Custom GraphQL wrapper requires an explicit data_path")
            key = "edges" if "edges" in connection else "nodes"
            nodes = connection[key]
            if not _iterable(nodes):
                raise ValueError(f"GraphQL {key} must be an array")
            for node in nodes:
                if key == "edges":
                    if not isinstance(node, Mapping) or "node" not in node:
                        raise ValueError("Each GraphQL edge must contain a node")
                    node = node["node"]
                if node is None:
                    counts["null_nodes"] += 1
                else:
                    yield from _expand(node, counts, depth + 1, record=True)
            return
        if record:
            yield value
            return
        for wrapper in _WRAPPERS:
            if wrapper in value and set(value).difference({wrapper}).issubset(_METADATA):
                wrapped = value[wrapper]
                if isinstance(wrapped, Mapping) or _iterable(wrapped):
                    yield from _expand(wrapped, counts, depth + 1)
                    return
        if all(_iterable(column) for column in value.values()):
            if len(value) > _MAX_FIELDS:
                raise ValueError(f"Input exceeds {_MAX_FIELDS} fields")
            for values in zip_longest(*(iter(column) for column in value.values()), fillvalue=_ABSENT):
                if any(item is _ABSENT for item in values):
                    raise ValueError("Column arrays must have equal length")
                yield dict(zip(value, values, strict=True))
            return
        yield value
    elif _iterable(value):
        for item in value:
            yield from _expand(item, counts, depth + 1, record=True)
    else:
        yield value


def _scalar(value: Any, counts: Counter[str]) -> Any:
    if isinstance(value, str):
        _utf8_size(value, _MAX_CELL_BYTES, "cell")
        return value
    if value is None or type(value) in (int, bool):
        return value
    if isinstance(value, float):
        if math.isfinite(value):
            return float(value)
        counts["nonfinite"] += 1
        return None
    if isinstance(value, Integral):
        return int(value)
    if isinstance(value, (Real, Decimal)):
        return _scalar(float(value), counts)
    if isinstance(value, (datetime, date, time)):
        return value.isoformat()
    if type(value).__module__.split(".", 1)[0] == "numpy" and hasattr(value, "item"):
        return _scalar(value.item(), counts)
    raise TypeError(f"Unsupported record value: {type(value).__name__}")


def _utf8_size(value: str, limit: int, label: str) -> int:
    if len(value) > limit:
        raise ValueError(f"Input {label} exceeds {limit} UTF-8 bytes")
    size = len(value) if value.isascii() else len(value.encode("utf-8"))
    if size > limit:
        raise ValueError(f"Input {label} exceeds {limit} UTF-8 bytes")
    return size


def _string_bytes(value: str, limit: int, label: str) -> int:
    size = _utf8_size(value, limit, label)
    if _JSON_ESCAPE.search(value):
        return len(json.dumps(value, ensure_ascii=False).encode("utf-8"))
    return size + 2


def _record_bytes(row: dict[str, Any]) -> int:
    """Count compact UTF-8 JSON incrementally, never serialize a whole wide row."""
    size = 2
    for index, (key, value) in enumerate(row.items()):
        size += _string_bytes(key, _MAX_FIELD_BYTES, "field name") + 1 + bool(index)
        if isinstance(value, str):
            size += _string_bytes(value, _MAX_CELL_BYTES, "cell")
        elif value is None:
            size += 4
        elif isinstance(value, bool):
            size += 4 if value else 5
        else:
            size += len(repr(value))
        if size > _MAX_RECORD_BYTES:
            raise ValueError(f"Input record exceeds {_MAX_RECORD_BYTES} compact UTF-8 JSON bytes")
    return size


def _check_retained_bytes(size: int) -> None:
    if size > _MAX_RETAINED_BYTES:
        raise ValueError(f"Normalized retained data exceeds {_MAX_RETAINED_BYTES} bytes")


def _flatten(value: Mapping[str, Any], counts: Counter[str]) -> dict[str, Any]:
    output: dict[str, Any] = {}

    def add(key: str, item: Any, depth: int) -> None:
        _utf8_size(key, _MAX_FIELD_BYTES, "field name")
        if depth > _MAX_DEPTH:
            raise ValueError("Record is nested too deeply or cyclic")
        if type(item) in _PRIMITIVES:
            pass
        elif isinstance(item, Mapping):
            for child, contents in item.items():
                if not isinstance(child, str) or not child:
                    raise ValueError("Record field names must be non-empty strings")
                add(f"{key}.{child}" if key else child, contents, depth + 1)
            return
        elif isinstance(item, (list, tuple)):
            for index, contents in enumerate(item):
                add(f"{key}.{index}", contents, depth + 1)
            return
        if key in output:
            raise ValueError(f"Flattened field collision: {key!r}")
        if len(output) >= _MAX_FIELDS:
            raise ValueError(f"Input exceeds {_MAX_FIELDS} fields")
        output[key] = _scalar(item, counts)

    for key, item in value.items():
        if not isinstance(key, str) or not key:
            raise ValueError("Record field names must be non-empty strings")
        add(key, item, 0)
    return output


def _records(
    data: Any, spec: ChartSpec, counts: Counter[str], schema: dict[str, int],
) -> Generator[tuple[dict[str, Any], int], None, None]:
    source = _source(data, spec.format)
    # Retain the adapter root even when path selection wraps it; never own caller input.
    owned = source if source is not data else None
    try:
        if spec.data_path is not None:
            tokens = spec.data_path.split(".")
            if any(not token for token in tokens):
                raise ValueError("data_path must contain non-empty dot-separated components")
            source = _select_path(source, tokens, counts)
        requested = tuple(dict.fromkeys(field for field in (spec.x, spec.y, spec.color, spec.size) if field))
        had_rows = False
        for index, item in enumerate(_expand(source, counts)):
            had_rows = True
            row = _flatten(item, counts) if isinstance(item, dict) or isinstance(item, Mapping) else {
                "index": index, "value": _scalar(item, counts),
            }
            for key, value in row.items():
                mask = 1 if type(value) in (int, float) else 2 if isinstance(value, str) else 4 if value is not None else 0
                schema[key] = schema.get(key, 0) | mask
            if len(schema) > _MAX_FIELDS:
                raise ValueError(f"Input schema exceeds {_MAX_FIELDS} fields")
            for field in requested:
                if field not in row:
                    counts["missing"] += 1
                    row[field] = None
            yield row, _record_bytes(row)
        if spec.data_path is not None and not counts["path_matches"] and (
            not counts["path_empty"] or counts["path_missing"]
        ):
            raise ValueError(f"data_path {spec.data_path!r} did not match any input")
        if counts["path_matches"] or spec.data_path is None:
            missing = [field for field in requested if field not in schema]
            if missing and had_rows:
                raise ValueError(f"Requested fields are missing from input: {', '.join(missing)}")
    finally:
        close = getattr(owned, "close", None)
        if close is not None:
            close()


def _plan(spec: ChartSpec, prefix: list[dict[str, Any]]) -> tuple[str, list[str], str]:
    numeric = [key for row in prefix for key, value in row.items() if type(value) in (int, float)]
    categorical = [key for row in prefix for key, value in row.items() if isinstance(value, (str, bool))]
    strategy = spec.aggregation
    if spec.kind == "heatmap":
        coordinates = list(dict.fromkeys(key for row in prefix for key in row if key != spec.color))
        x = spec.x if spec.x is not None else next((key for key in coordinates if key != spec.y), None)
        y = spec.y if spec.y is not None else next((key for key in coordinates if key != x), None)
        groups = list(dict.fromkeys(field for field in (x, y) if field is not None))
        measure = spec.color or "count"
        if strategy == "auto":
            strategy = "sum" if spec.color is not None else "count"
        if strategy in _REDUCTIONS:
            if prefix and len(groups) != 2:
                raise ValueError("Heatmaps require distinct x and y coordinate fields")
            if strategy != "count" and spec.color is None:
                raise ValueError("Numeric heatmap reductions require a color measure field")
    else:
        scalar_rows = bool(prefix) and all(row.keys() == {"index", "value"} for row in prefix)
        if scalar_rows and spec.x is None:
            x = "value" if "value" in categorical and "value" not in numeric else None
        else:
            x = spec.x if spec.x is not None else next(iter(categorical), None)
        inferred = next((key for key in numeric if key != x and not (scalar_rows and key == "index")), None)
        y = spec.y if spec.y is not None else inferred
        if strategy == "auto":
            if spec.kind in _CATEGORICAL and x in categorical:
                strategy = "sum" if y is not None else "count"
            else:
                strategy = "none"
        if strategy in _REDUCTIONS and y is None and strategy != "count":
            raise ValueError(f"Aggregation {strategy!r} requires a numeric y field")
        groups = list(dict.fromkeys(field for field in (x, spec.color) if field is not None))
        measure = "count" if strategy == "count" and spec.y is None else y or "count"
    if strategy in _REDUCTIONS and measure in groups:
        raise ValueError("The reduction measure must differ from grouping fields")
    if strategy in _REDUCTIONS and spec.size is not None and spec.size not in [*groups, measure]:
        raise ValueError("Reduction would remove the mapped size field; use aggregation='sample' or 'none'")
    return strategy, groups, measure


def _sum_units(value: int | float) -> int:
    """Represent a finite number as integer multiples of the smallest subnormal."""
    numerator, denominator = value.as_integer_ratio()
    return numerator << (1074 - (denominator.bit_length() - 1))


class _Reducer:
    """Keep at most limit group states; no set of overflow keys is retained."""

    def __init__(self, strategy: str, fields: list[str], measure: str, limit: int, counts: Counter[str]):
        self.strategy = strategy
        self.fields = fields
        self.measure = measure
        self.limit = limit
        self.counts = counts
        self.groups: dict[tuple[Any, ...], list[Any]] = {}
        self.other: list[Any] | None = None
        self.retained_bytes = 2

    def _store(self, state: list[Any], value: Any, correction: Any = 0, exponent: int = 0) -> None:
        size = 128
        if any(isinstance(item, int) and item.bit_length() > 96 for item in (state[0], value, correction)):
            size = max(size, sum(len(repr(item)) for item in (state[0], value, correction, exponent)))
        retained = self.retained_bytes + size - state[4]
        _check_retained_bytes(retained)
        self.retained_bytes = retained
        state[1:] = [value, correction, exponent, size]

    def add(self, row: dict[str, Any]) -> None:
        # JSON numbers share numeric equality; booleans/strings remain distinct.
        key = tuple(
            (float if type(row.get(field)) in (int, float) else type(row.get(field)), row.get(field))
            for field in self.fields
        )
        state = self.groups.get(key)
        if state is None:
            if self.other is not None:
                state = self.other
            elif len(self.groups) < self.limit:
                # Reserve numeric-state overhead as well as retained category strings.
                self.retained_bytes += _record_bytes(
                    {field: row.get(field) for field in self.fields} | {self.measure: None}
                ) + 129
                _check_retained_bytes(self.retained_bytes)
                state = [0, None, 0, 0, 128]
                self.groups[key] = state
            else:
                last = next(reversed(self.groups))
                self.other = self.groups.pop(last)
                state = self.other
                self.counts["overflow"] = 1
        if self.strategy == "count":
            state[0] += 1
            self._store(state, state[0])
            return
        value = row.get(self.measure)
        if value is None or type(value) not in (int, float):
            if value is not None:
                self.counts["nonnumeric"] += 1
            return
        state[0] += 1
        correction, exponent = state[2:4]
        if self.strategy == "sum" and exponent == -1074:
            self._store(state, state[1] + _sum_units(value), exponent=-1074)
            return
        if self.strategy == "mean" and exponent:
            value = math.ldexp(value, -exponent)
        previous = state[1]
        if previous is None:
            total = value
        elif self.strategy in {"sum", "mean"}:
            total = previous + value
            if self.strategy == "sum" and isinstance(total, float) and not math.isfinite(total):
                # Promote only overflowing sums; one budgeted integer, never a partial/input list.
                units = _sum_units(previous) + _sum_units(correction) + _sum_units(value)
                self._store(state, units, exponent=-1074)
                return
            if self.strategy == "mean" and isinstance(total, float) and not math.isfinite(total):
                # Scale the numerator by powers of two; the finite mean need not overflow.
                previous = math.ldexp(previous, -1)
                value = math.ldexp(value, -1)
                correction = math.ldexp(correction, -1)
                exponent += 1
                total = previous + value
            if not isinstance(total, float) or math.isfinite(total):
                # Neumaier compensation also survives transfer into the other bucket.
                correction += (
                    (previous - total) + value if abs(previous) >= abs(value)
                    else (value - total) + previous
                )
        elif self.strategy == "min":
            total = min(previous, value)
        else:
            total = max(previous, value)
        self._store(state, total, correction, exponent)

    def finish(self) -> list[dict[str, Any]]:
        def result(state: list[Any]) -> Any:
            value = state[1]
            if self.strategy == "sum" and value is not None:
                if state[3] == -1074:
                    try:
                        value = value / (1 << 1074)
                    except OverflowError:
                        value = math.inf
                else:
                    value += state[2]
            elif self.strategy == "mean" and value is not None:
                try:
                    value = math.ldexp(value / state[0] + state[2] / state[0], state[3])
                except OverflowError:
                    value = math.inf
            return _scalar(value, self.counts)

        records = [
            dict(zip(self.fields, (part[1] for part in key), strict=True)) | {self.measure: result(state)}
            for key, state in self.groups.items()
        ]
        if self.other is not None:
            label = "__deepviz_other__"
            labels = {part[1] for key in self.groups for part in key}
            while label in labels:
                label += "_"
            records.append(dict.fromkeys(self.fields, label) | {self.measure: result(self.other)})
        return records


def normalize(data: Any, spec: ChartSpec | dict[str, Any]) -> NormalizedData:
    """Normalize a finite input, consuming streams once with bounded retained state.

    Raises ValueError/TypeError for malformed data, invalid field mappings or
    unsupported cell values. File errors remain ordinary OSError subclasses.
    Retained compact UTF-8 JSON/state is capped at 16 MiB; string cells at
    64 KiB, field names at 4 KiB and records at 256 KiB. Oversize data raises ValueError,
    never silent truncation. These are payload budgets, not process RSS limits.
    Additional memory includes a <=32-row inference prefix (stopped after
    reaching 16 MiB), schema state, and a 4096-row columnar conversion batch.
    Schema width is capped at 1024 fields and nesting at 64 levels.
    Automatic mappings and strategy are chosen from that prefix; use explicit
    x/y/aggregation for heterogeneous streams whose early rows are unrepresentative.
    Record collections retain nested arrays as fields; column inference applies
    to top-level mappings. Equal int/float categories share numeric identity,
    separate from booleans/strings, preserving the first display representative.
    Cross-language integer precision is only guaranteed in JavaScript's safe
    integer range, even though Python's integer reductions remain exact beyond it.
    """
    if not isinstance(spec, (ChartSpec, dict)):
        raise TypeError("spec must be a ChartSpec or dictionary")
    spec = spec if isinstance(spec, ChartSpec) else ChartSpec.model_validate(spec)
    if any(field is not None and not field.strip() for field in (spec.x, spec.y, spec.color, spec.size)):
        raise ValueError("Mapped field names must not be empty")
    counts: Counter[str] = Counter()
    schema: dict[str, int] = {}
    rows = _records(data, spec, counts, schema)
    try:
        prefix = []
        prefix_bytes = 0
        for row, size in islice(rows, 32):
            prefix.append((row, size))
            prefix_bytes += size
            if prefix_bytes >= _MAX_RETAINED_BYTES:
                break
        strategy, fields, measure = _plan(spec, [row for row, _ in prefix])
        input_count = 0
        if strategy in _REDUCTIONS:
            reducer = _Reducer(strategy, fields, measure, spec.max_points, counts)
            for row, _ in chain(prefix, rows):
                input_count += 1
                reducer.add(row)
            records = reducer.finish()
        else:
            rng = random.Random(0)
            reservoir: list[tuple[int, dict[str, Any], int]] = []
            retained_bytes = 2
            for row, size in chain(prefix, rows):
                input_count += 1
                if input_count <= spec.max_points:
                    retained_bytes += size + bool(reservoir)
                    _check_retained_bytes(retained_bytes)
                    reservoir.append((input_count, row, size))
                else:
                    slot = rng.randrange(input_count)
                    if slot < spec.max_points:
                        retained_bytes += size - reservoir[slot][2]
                        _check_retained_bytes(retained_bytes)
                        reservoir[slot] = (input_count, row, size)
            records = [row for _, row, _ in sorted(reservoir)]
            if input_count > spec.max_points:
                strategy = "sample"
    finally:
        rows.close()
    _check_retained_bytes(2 + sum(_record_bytes(row) for row in records) + max(0, len(records) - 1))
    warnings = []
    if strategy == "sample" and input_count > spec.max_points:
        warnings.append(
            f"Deterministic reservoir sample: {len(records)} of {input_count} rows; "
            f"max_points={spec.max_points} overrides aggregation={spec.aggregation!r}. "
            "Original source order is preserved, but sampling may miss peaks/extrema and short-lived events."
        )
    if counts["overflow"]:
        warnings.append(
            f"Group cardinality exceeded max_points={spec.max_points}; first {spec.max_points - 1} groups "
            "are exact and all non-retained groups contribute to the final other bucket (including weighted mean)."
        )
    messages = {
        "nonfinite": "non-finite numeric values replaced by null",
        "missing": "missing mapped field values filled with null",
        "nonnumeric": "non-numeric measure values excluded from reduction",
        "null_nodes": "null GraphQL/path nodes skipped",
        "path_missing": "data_path branches with missing components skipped",
        "graphql_errors": "GraphQL responses contained errors alongside usable data",
    }
    warnings.extend(f"{counts[key]} {message}." for key, message in messages.items() if counts[key])
    mixed = [key for key, mask in schema.items() if mask & 1 and mask & 6]
    if mixed:
        warnings.append(f"Fields contain mixed numeric/non-numeric values: {', '.join(mixed)}.")
    return NormalizedData(records=records, input_count=input_count, warnings=warnings, strategy=strategy)
