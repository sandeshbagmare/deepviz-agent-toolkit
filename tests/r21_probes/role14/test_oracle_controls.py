"""Oracle negative controls; no browser/network/product assumptions."""
import importlib.util
from pathlib import Path

import pytest

SPEC = importlib.util.spec_from_file_location('r21_contract_control', Path(__file__).with_name('host_contract.py'))
assert SPEC and SPEC.loader
contract = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(contract)


def good_case():
    return {'state': {'readyThenType': 'function', 'renderError': 'runtime missing'},
            'naive_await_ready_outcome': 'rejected:runtime missing'}


def test_explicit_rejected_promise_and_declared_error_is_accepted():
    assert contract.failure_problems(good_case()) == []


@pytest.mark.parametrize('fault', ['no-promise', 'false-fulfill', 'no-error'])
def test_missing_runtime_signal_is_never_green(fault):
    case = good_case()
    if fault == 'no-promise':
        case['state']['readyThenType'] = 'undefined'
    elif fault == 'false-fulfill':
        case['naive_await_ready_outcome'] = 'fulfilled'
    else:
        case['state']['renderError'] = None
    assert len(contract.failure_problems(case)) == 1
