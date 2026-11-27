"""Validate actual public TS tool schemas using the existing read-only environment."""

import importlib.metadata
import json
import sys

from jsonschema import Draft202012Validator


def main() -> None:
    payload = json.load(sys.stdin)
    tools = payload["tools"]
    request = payload["request"]
    expected = [True, False, False]
    assert len(tools) == 5
    for tool in tools:
        schema = tool["inputSchema"]
        Draft202012Validator.check_schema(schema)
        validator = Draft202012Validator(schema)
        actual = [
            validator.is_valid(request),
            validator.is_valid({"spec": request["spec"]}),
            validator.is_valid({**request, "filePath": "not-authorized"}),
        ]
        assert actual == expected, (tool["name"], actual)
    print(
        json.dumps(
            {
                "validator": "Draft202012Validator",
                "jsonschema_version": importlib.metadata.version("jsonschema"),
                "schemas_checked": len(tools),
                "each_schema_controls": expected,
            }
        )
    )


if __name__ == "__main__":
    main()
