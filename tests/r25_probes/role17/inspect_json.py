"""Save literal public-model JSON output/error inspections, separate from pytest totals."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator
from pydantic import ValidationError

import deepviz.models as models


def main():
    identity_path = Path(sys.argv[1]).resolve(strict=True)
    identity = json.loads(identity_path.read_text(encoding="utf-8"))
    source = identity_path.parent
    assert identity["product_source_sha"] == "99841ffb80e0f2ea90c753c1bf0ceff718e0e180"
    actual_file = Path(models.__file__).resolve()
    assert actual_file == Path(identity["actual_model_path"]).resolve()
    for row in identity["source_files"]:
        assert hashlib.sha256((source / row["path"]).read_bytes()).hexdigest() == row["sha256"]
    schema = models.ChartSpec.model_json_schema()
    assert schema == json.loads((source / "schemas/chart-spec.schema.json").read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema)
    fixtures = [
        ("defaults", "{}", True, False, {"version": 1, "width": 900, "height": 520, "columns": 2, "max_points": 2000}),
        ("integral-json-floats", '{"version":1.0,"width":900.0,"height":520.0,"columns":2.0,"max_points":2000.0}',
         True, False, {"version": 1, "width": 900, "height": 520, "columns": 2, "max_points": 2000}),
        ("mixed-valid-bounds", '{"version":1,"width":240,"height":4096,"columns":6,"max_points":100000}',
         True, False, {"version": 1, "width": 240, "height": 4096, "columns": 6, "max_points": 100000}),
        ("dashboard-child-integral-floats", '{"kind":"dashboard","charts":[{"version":1.0,"width":900.0,"height":200.0,"columns":1.0,"max_points":10.0}]}',
         True, True, {"version": 1, "width": 900, "height": 200, "columns": 1, "max_points": 10}),
    ]
    for field, string_token in (("version", '"1"'), ("width", '"900"'), ("height", '"520"'),
                                ("columns", '"2"'), ("max_points", '"2000"')):
        for label, token in (("boolean", "true"), ("numeric-string", string_token)):
            raw = '{"kind":"dashboard","charts":[{"' + field + '":' + token + '}]}'
            fixtures.append(("child-" + field + "-" + label, raw, False, True, None))
    fixtures.append(("child-unknown-code-key", '{"kind":"dashboard","charts":[{"code":"not executable"}]}',
                     False, True, None))
    outputs = []
    for label, raw, expected, child, wanted in fixtures:
        parsed_json = json.loads(raw)
        row = {"label": label, "raw_json": raw, "expected_accepted": expected,
               "schema_accepted": validator.is_valid(parsed_json)}
        try:
            value = models.ChartSpec.model_validate_json(raw)
        except ValidationError as error:
            row.update(model_accepted=False, errors=error.errors(include_context=False, include_url=False))
            if child:
                assert all(entry["loc"][0:2] == ("charts", 0) for entry in row["errors"])
        else:
            row.update(model_accepted=True, serialized_json=value.model_dump_json(),
                       serialized_value=value.model_dump(mode="json"))
            target = value.charts[0] if child else value
            assert wanted is not None
            assert {key: getattr(target, key) for key in wanted} == wanted
            assert all(type(getattr(target, key)) is int for key in wanted)
            assert validator.is_valid(row["serialized_value"])
            assert models.ChartSpec.model_validate_json(row["serialized_json"]) == value
        assert row["model_accepted"] is expected and row["schema_accepted"] is expected
        outputs.append(row)
    output = {"source": identity["product_source_sha"], "actual_public_module_file": str(actual_file),
              "actual_public_model_sha256": hashlib.sha256(actual_file.read_bytes()).hexdigest(),
              "inspection_kind": "15 serialized/error-output inspections, NOT additional pytest cases",
              "accepted": 4, "rejected": 11, "outputs": outputs}
    Path(sys.argv[2]).write_text(json.dumps(output, indent=2, ensure_ascii=False), encoding="utf-8", newline="\n")
    print(json.dumps({"source": identity["product_source_sha"], "real_public_JSON_inspections": 15,
                      "accepted": 4, "rejected": 11, "all_literal_oracles_and_schema_agree": True}))


if __name__ == "__main__":
    main()
