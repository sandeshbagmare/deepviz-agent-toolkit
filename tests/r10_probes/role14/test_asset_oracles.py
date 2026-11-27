"""Independent negative controls for the portable manifest oracle, not production changes."""
import importlib.util
from pathlib import Path

import pytest

SPEC = importlib.util.spec_from_file_location('role14_asset_manifest', Path(__file__).with_name('asset_manifest.py'))
assert SPEC and SPEC.loader
probe = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(probe)


def test_exact_echarts_pin_accepted():
    html = '<script src="https://cdn.jsdelivr.net/npm/echarts@6.1.0/dist/echarts.min.js"></script>'
    assert probe.validate_html(html, 'echarts').scripts == probe.PINS['echarts']


@pytest.mark.parametrize('pin', ['5.6.0', '6', 'latest', '^6.1.0'])
def test_wrong_or_floating_pin_rejected(pin):
    with pytest.raises(AssertionError):
        probe.validate_html(f'<script src="https://cdn.jsdelivr.net/npm/echarts@{pin}/dist/echarts.min.js"></script>', 'echarts')


def test_python_plotly_must_not_reintroduce_cdn():
    with pytest.raises(AssertionError):
        probe.validate_html('<script src="https://cdn.plot.ly/plotly-3.7.0.min.js"></script>', 'plotly', 'notice')


def test_notice_must_be_complete_not_only_a_link_or_fragment():
    with pytest.raises(AssertionError, match='Incomplete notice'):
        probe.validate_html('<!--MIT permission-->', 'plotly', 'MIT permission warranty')
    assert probe.validate_html('<!--MIT\npermission\nwarranty-->', 'plotly', 'MIT permission warranty').scripts == []
