"""Strict live host oracles. Deliberate source defects remain RED, never xfail."""
import importlib.util
from pathlib import Path

import pytest

SPEC = importlib.util.spec_from_file_location('r21_contract', Path(__file__).with_name('host_contract.py'))
assert SPEC and SPEC.loader
contract = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(contract)


@pytest.mark.parametrize('engine', ['echarts', 'antv'])
def test_denied_interactive_runtime_has_rejected_ready_and_declared_error(cases, engine):
    case = cases[engine + '-denied']
    problems = contract.failure_problems(case)
    assert not problems, '; '.join(problems)


@pytest.mark.parametrize('name', ['echarts-denied', 'antv-denied', 'matplotlib-static-offline',
                                 'echarts-existing-local-runtime', 'antv-existing-local-runtime'])
def test_fallback_keeps_two_literal_records_and_is_keyboard_accessible(cases, name):
    case = cases[name]
    assert case['state']['tableCells'] == ['A & B', '3', 'C < D', '9']
    assert case['state']['literalElements'] == 0
    assert 'table' in case['keyboard_opened_accessible_snapshot']
    assert 'A & B' in case['keyboard_opened_accessible_snapshot']
    assert 'C < D' in case['keyboard_opened_accessible_snapshot']
    assert case['unexpected_requests'] == []


@pytest.mark.parametrize('name', ['matplotlib-static-offline', 'echarts-existing-local-runtime', 'antv-existing-local-runtime'])
def test_real_positive_controls_have_no_errors_and_actual_graphic(cases, name):
    case = cases[name]
    assert case['resource_failures'] == case['page_errors'] == case['unexpected_console_errors'] == []
    assert case['expected_fixture_ERR_FAILED'] == case['blocked'] == []
    if name.startswith('matplotlib'):
        assert case['local_runtime_supplied'] == []
        assert case['state']['images'][0]['complete'] and case['state']['images'][0]['width'] > 0
    else:
        assert case['host_promise_discovery'] == 'promise-present'
        assert case['naive_await_ready_outcome'] == 'fulfilled'
        assert case['state']['chartGraphics'] > 0
