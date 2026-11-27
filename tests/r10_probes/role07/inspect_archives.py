"""Check fresh wheel/sdist bytes and wheel RECORD against the exact Git snapshot."""
from __future__ import annotations

import base64
import configparser
import csv
import hashlib
import io
import json
import sys
import tarfile
import zipfile
from pathlib import Path


def main() -> None:
    source, wheel_path, sdist_path, output = map(Path, sys.argv[1:])
    checks = []
    members = []
    package = source / "python/deepviz/src/deepviz"
    with zipfile.ZipFile(wheel_path) as wheel:
        names = wheel.namelist()
        assert len(names) == len(set(names))
        checks.append("unique wheel members")
        for path in sorted(package.rglob("*")):
            if path.is_file():
                name = "deepviz/" + path.relative_to(package).as_posix()
                assert wheel.read(name) == path.read_bytes(), name
                checks.append("wheel exact source " + name)
        for path in sorted((source / "prompts/v1").glob("*.md")):
            assert wheel.read("deepviz/resources/prompts/v1/" + path.name) == path.read_bytes()
            checks.append("wheel exact prompt " + path.name)
        assert wheel.read("deepviz/resources/chart-spec.schema.json") == (
            source / "schemas/chart-spec.schema.json").read_bytes()
        checks.append("wheel exact schema")
        points = configparser.ConfigParser()
        points.read_string(wheel.read(next(name for name in names if name.endswith("/entry_points.txt"))).decode())
        assert dict(points["console_scripts"]) == {
            "deepviz": "deepviz.cli:main", "deepviz-mcp": "deepviz.mcp_server:main",
        }
        checks.append("two exact console entrypoints")
        license_name = next(name for name in names if name.endswith(".dist-info/licenses/LICENSE"))
        assert wheel.read(license_name) == (source / "LICENSE").read_bytes()
        checks.append("wheel exact LICENSE")
        record = next(name for name in names if name.endswith("/RECORD"))
        for name, digest, size in csv.reader(io.StringIO(wheel.read(record).decode())):
            if not digest:
                assert name == record
                continue
            content = wheel.read(name)
            actual = base64.urlsafe_b64encode(hashlib.sha256(content).digest()).rstrip(b"=").decode()
            assert digest == "sha256=" + actual and int(size) == len(content), name
        checks.append("all wheel RECORD hashes/sizes")
        for name in names:
            data = wheel.read(name)
            members.append({"archive": "wheel", "member": name, "bytes": len(data),
                            "sha256": hashlib.sha256(data).hexdigest()})
    with tarfile.open(sdist_path) as sdist:
        files = [member for member in sdist.getmembers() if member.isfile()]
        prefix = files[0].name.split("/")[0] + "/"
        for member in files:
            assert member.name.startswith(prefix)
            relative = member.name[len(prefix):]
            member_stream = sdist.extractfile(member)
            assert member_stream is not None
            data = member_stream.read()
            if relative != "PKG-INFO":
                assert data == (source / relative).read_bytes(), relative
            members.append({"archive": "sdist", "member": member.name, "bytes": len(data),
                            "sha256": hashlib.sha256(data).hexdigest()})
        for required in ("pyproject.toml", "schemas/chart-spec.schema.json", "prompts/v1/system.md",
                         "prompts/v1/request.md", "python/deepviz/src/deepviz/py.typed"):
            assert any(member.name == prefix + required for member in files), required
            checks.append("sdist source inclusion " + required)
        checks.append("all sdist files equal exact checkpoint snapshot, except generated PKG-INFO")
        checks.append("sdist has no files absent from the exact checkpoint snapshot (except PKG-INFO)")
    result = {"passed": len(checks), "failed": 0, "skipped": 0, "checks": checks,
              "wheel_members": len(names), "sdist_files": len(files), "members": members}
    with output.open("x", encoding="utf-8") as stream:
        json.dump(result, stream, indent=2)
        stream.write("\n")
    print(json.dumps({key: result[key] for key in ("passed", "failed", "skipped", "wheel_members", "sdist_files")}))


if __name__ == "__main__":
    main()
