"""Finite independent GraphQL fixtures, separate from production shape inference."""
from __future__ import annotations

import copy
import json
from collections.abc import Iterator
from pathlib import Path
from typing import Any

CORPUS = json.loads(Path(__file__).with_name("corpus.json").read_text(encoding="utf-8"))
RAW = {"kind": "table", "aggregation": "none", "max_points": 100}


def connection(rows: list[Any], key: str, *, finished: bool = False) -> dict[str, Any]:
    values = [{"node": row, "cursor": f"opaque-{index}"} for index, row in enumerate(rows)] if key == "edges" else rows
    return {key: values, "totalCount": 987654321,
            "pageInfo": {"hasNextPage": not finished, "endCursor": "same-cursor"}}


def page(rows: list[Any], key: str, *, finished: bool = False) -> dict[str, Any]:
    return {"data": {"feed": connection(rows, key, finished=finished)}}


def success(name: str) -> tuple[Any, dict[str, Any], list[dict[str, Any]], list[str]]:
    first = [copy.deepcopy(CORPUS["repeat"]) for _ in range(2)]
    tail = [copy.deepcopy(CORPUS[key]) for key in ("repeat", "distinct", "repeat")]
    modes = ("edges", "nodes", "edges") if name == "mixed-auto" else ("edges",) * 3 if name == "edges-auto" else ("nodes",) * 3
    # Deliberately false first-page hasNextPage: supplied pages still must all be consumed.
    pages = [page(first, modes[0], finished=True), page([], modes[1]), page(tail, modes[2], finished=True)]
    spec = dict(RAW)
    expected = copy.deepcopy(CORPUS["expected_five"])
    notices: list[str] = []
    if name == "nested-select":
        pages = [{"data": {"buckets": [{"feed": connection(rows, "edges")}],
                           "shadow": {"edges": [{"cursor": "invalid-unselected"}]}}}
                 for rows in (first, [], tail)]
        spec["data_path"] = "data.buckets.feed.edges.node"
    elif name == "siblings-select":
        for item in pages:
            item["data"]["shadow"] = {"edges": [{"cursor": "invalid-unselected"}]}
        spec["data_path"] = "data.feed.nodes"
    elif name == "pages-envelope-select":
        spec["data_path"] = "pages.data.feed.nodes"
        return {"pages": pages}, spec, expected, notices
    elif name == "warnings-late":
        pages[-1]["data"]["feed"]["nodes"] += [None, None]
        pages[-1]["errors"] = [{"message": "unselected resolver unavailable"}]
        notices = ["null", "graphql"]
    elif name == "missing-branch-select":
        pages[1] = {"data": {}}
        spec["data_path"] = "data.feed.nodes"
        notices = ["missing"]
    elif name == "all-empty":
        pages = [page([], key) for key in ("edges", "nodes", "edges")]
        expected = []
    return pages, spec, expected, notices


def late_fault(name: str, selected: bool) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    pages = [page([{"id": index, "measure": index / 4} for index in range(40)], "nodes"),
             page([], "nodes")]
    bad: dict[str, Any] = ({"data": {"feed": {"edges": [{"cursor": "missing-node"}]}}} if name == "edge-without-node"
           else page([{"a.b": 1, "a": {"b": 2}}], "nodes") if name == "node-field-collision"
           else {"data": None, "errors": [{"message": "late page unavailable"}]})
    if name == "error-only-no-data":
        bad.pop("data")
    elif name == "error-only-empty-data":
        bad["data"] = {}
    pages.append(bad)
    return pages, dict(RAW, **({"data_path": "data.feed"} if selected else {}))


def sibling_pages(name: str) -> list[dict[str, Any]]:
    key, variant = name.split("-")
    pages, _ = late_fault("node-field-collision", False)
    bad = connection([{"id": "selected-only"}], key)
    bad["audit"] = 7 if variant == "scalar" else {"source": "must-not-disappear"}
    pages[-1] = {"data": {"feed": bad}}
    return pages


class PullPages(Iterator[Any]):
    """Public one-shot source; count consumption, never assert lifecycle closure."""

    def __init__(self, values: list[Any], *, poison_after: int | None = None) -> None:
        self.values = values
        self.pulled: list[int] = []
        self.poison_after = poison_after
        self.finished = False

    def __iter__(self) -> PullPages:
        return self

    def __next__(self) -> Any:
        index = len(self.pulled)
        if self.poison_after is not None and index >= self.poison_after:
            raise AssertionError("overread a page after the invalid late node")
        if index == len(self.values):
            self.finished = True
            raise StopIteration
        self.pulled.append(index)
        return self.values[index]
