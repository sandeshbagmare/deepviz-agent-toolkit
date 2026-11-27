"""Independent anti-weakening regressions: no renderer or existing-oracle edits."""
from __future__ import annotations

import copy
import json
import subprocess
import sys
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path

import pytest
from vega_contract import (
    CHILDREN,
    NS,
    PARENT,
    assert_dashboard,
    assert_geometry_values,
    assert_inert_svg,
    assert_native_children,
    assert_visible_title,
    make_dashboard,
    make_strict,
)


@pytest.fixture(scope="module")
def ordinary(tmp_path_factory):
    return make_dashboard(tmp_path_factory.mktemp("role17-original"))


def change_title(svg: str, title: str, replacement: str) -> ET.Element:
    root = ET.fromstring(svg)
    matches = [node for node in root.iter() if node.tag == NS + "text" and node.text == title]
    assert len(matches) == 1
    matches[0].text = replacement
    return root


@pytest.mark.parametrize("theme", ("light", "dark"))
@pytest.mark.parametrize("form", ("records", "columns", "nested_json", "graphql", "csv"))
def test_real_parent_correct_children_and_irregular_native_geometry(tmp_path: Path, theme: str, form: str):
    assert_dashboard(make_dashboard(tmp_path, theme, form))


@pytest.mark.parametrize("title", (PARENT, *CHILDREN))
def test_metadata_only_cannot_replace_any_visible_title(ordinary, title: str):
    root = change_title(ordinary.svg, title, "VISIBLE TITLE REMOVED")
    ET.SubElement(root, NS + "title").text = title
    ET.SubElement(root, NS + "desc").text = title
    root.append(ET.Comment(title))
    svg = ET.tostring(root, encoding="unicode")
    assert title in "".join(root.itertext()), "control must retain misleading metadata"
    with pytest.raises(AssertionError, match="required visible text missing"):
        assert_visible_title(svg, title)


@pytest.mark.parametrize("style", ({"display": "none"}, {"visibility": "hidden"}, {"opacity": "0"}))
def test_hidden_parent_title_is_not_visible_text(ordinary, style):
    root = ET.fromstring(ordinary.svg)
    matches = [node for node in root.iter() if node.tag == NS + "text" and node.text == PARENT]
    assert len(matches) == 1
    matches[0].set("style", ";".join(f"{key}:{value}" for key, value in style.items()))
    with pytest.raises(AssertionError, match="required text is hidden"):
        assert_visible_title(ET.tostring(root, encoding="unicode"), PARENT)


def test_parent_title_is_not_a_valid_standalone_child_oracle(ordinary):
    wrong = copy.deepcopy(ordinary.manifest)
    wrong["native_specs"][0]["title"] = PARENT
    with pytest.raises(AssertionError, match="wrong child title/scope"):
        assert_native_children(wrong)


@pytest.mark.parametrize("child", (0, 1))
def test_native_value_corruption_is_rejected(ordinary, child):
    wrong = copy.deepcopy(ordinary.manifest)
    native = wrong["native_specs"][child]
    native["data"]["values"][0][native["encoding"]["y"]["field"]] = 999
    with pytest.raises(AssertionError, match="native mapped values changed"):
        assert_native_children(wrong)


@pytest.mark.parametrize("role", ("bar", "point"))
def test_correct_metadata_does_not_excuse_wrong_drawn_geometry(ordinary, role):
    root = ET.fromstring(ordinary.svg)
    mark = next(node for node in root.iter() if node.get("aria-roledescription") == role)
    mark.set("d" if role == "bar" else "transform",
             "M1,0h20v240h-20Z" if role == "bar" else "translate(999,999)")
    with pytest.raises(AssertionError):
        assert_geometry_values(ET.tostring(root, encoding="unicode"), ordinary.manifest)


@pytest.mark.parametrize("attack", ("script", "foreignObject", "onload", "external-href", "style"))
def test_executable_foreign_and_external_svg_controls_are_rejected(ordinary, attack):
    root = ET.fromstring(ordinary.svg)
    if attack == "onload":
        root.set("onload", "window.__DV_XSS__=99")
    elif attack == "external-href":
        ET.SubElement(root, NS + "use").set("href", "https://example.invalid/never-fetched")
    else:
        ET.SubElement(root, NS + attack).text = "window.__DV_XSS__=99"
    with pytest.raises(AssertionError):
        assert_inert_svg(ET.tostring(root, encoding="unicode"))


class WrapperAudit(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.tags = []

    def handle_starttag(self, tag, attrs):
        self.tags.append((tag, dict(attrs)))


def test_distinct_malicious_title_field_and_category_remain_literal_text(tmp_path: Path):
    output = make_strict(tmp_path)
    for value in (PARENT, *CHILDREN, "label </script><script>alert(1)</script>", "<img onerror=x>"):
        assert_visible_title(output.svg, value)
    parser = WrapperAudit()
    parser.feed(output.html_path.read_text(encoding="utf-8"))
    assert not any(tag in {"script", "iframe", "object", "embed"} for tag, _ in parser.tags)
    assert not any(name.lower().startswith("on") for _, attrs in parser.tags for name in attrs)
    assert [attrs["src"] for tag, attrs in parser.tags if tag == "img"] == ["chart.svg"]


def test_cli_relative_output_is_portable_from_another_directory(tmp_path: Path):
    script = Path(__file__).with_name("vega_contract.py")
    result = subprocess.run([sys.executable, str(script), "--output", "relative-smoke"], cwd=tmp_path,
                            capture_output=True, text=True, timeout=120, check=False)
    assert result.returncode == 0, result.stderr
    summary = json.loads((tmp_path / "relative-smoke/summary.json").read_text(encoding="utf-8"))
    assert (summary["input_count"], summary["output_count"]) == (3, 6)
    assert (tmp_path / "relative-smoke/composed.svg").is_file()
    assert (tmp_path / "relative-smoke/composed.png").is_file()
