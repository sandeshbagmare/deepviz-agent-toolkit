"""Read-only Python controls for the cross-language GraphQL error carrier diagnostic."""
from __future__ import annotations

import hashlib
import importlib
import json
import sys
from dataclasses import asdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from graphql_fixtures import RAW, PullPages, late_fault, page

from deepviz.normalize import normalize


def main() -> None:
    destination = Path(sys.argv[1] if len(sys.argv) > 1 else "artifacts/r15-03/python-carrier-diagnostic.json")
    observations: list[dict[str, Any]] = []
    for variant in ("null-data", "no-data", "empty-data"):
        failed = {"errors": [{"message": "late page unavailable"}]}
        if variant != "no-data":
            failed["data"] = None if variant == "null-data" else {}
        for carrier in ("direct", "list", "json", "iterator", "explicit"):
            pages, _ = late_fault("error-only-response", False)
            pages[2] = failed
            try:
                spec = dict(RAW)
                data: Any = failed if carrier == "direct" else pages
                if carrier == "iterator":
                    data = PullPages(pages)
                elif carrier == "json":
                    data = json.dumps(pages)
                    spec["format"] = "json"
                elif carrier == "explicit":
                    spec["data_path"] = "data.feed"
                result = normalize(data, spec)
                observations.append({"variant": variant, "carrier": carrier, "outcome": "returned",
                                     **asdict(result)})
            except ValueError as error:
                observations.append({"variant": variant, "carrier": carrier, "outcome": "rejected",
                                     "error_type": type(error).__name__, "message": str(error)})
    data = {"pages": [page([{"id": "one"}], "nodes"), page([], "nodes"), page([{"id": "two"}], "nodes")]}
    for selected in (False, True):
        try:
            result = normalize(data, dict(RAW, **({"data_path": "pages.data.feed.nodes"} if selected else {})))
            observations.append({"variant": "N12-known-pages-wrapper-policy", "carrier": "explicit" if selected else "auto",
                                 "outcome": "returned", **asdict(result)})
        except ValueError as error:
            observations.append({"variant": "N12-known-pages-wrapper-policy", "carrier": "explicit" if selected else "auto",
                                 "outcome": "rejected", "message": str(error)})
    identity = {}
    for name in ("deepviz.normalize", "deepviz.models", "pytest"):
        path = Path(importlib.import_module(name).__file__).resolve()
        identity[name] = {"path": str(path), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
    result = {"recorded_at": datetime.now(UTC).isoformat(), "python": sys.executable,
              "version": sys.version, "identity": identity,
              "expected_source": "5340bc69b7203ad7a9166543062482d819f9b705", "observations": observations,
              "claim": "observed public controls; diagnostic exit0 is not full acceptance"}
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(f"OBSERVATIONS={len(observations)}; DIAGNOSTIC={destination}; ACCEPTANCE_NOT_CLAIMED=True")


if __name__ == "__main__":
    main()
