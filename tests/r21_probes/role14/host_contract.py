"""Read-only predicates for the intended blocked-runtime host failure invariant."""
from __future__ import annotations


def failure_problems(case: dict) -> list[str]:
    state = case['state']
    problems = []
    if state['readyThenType'] != 'function':
        problems.append('blocked interactive runtime did not expose a settled readiness Promise')
    if not case['naive_await_ready_outcome'].startswith('rejected:'):
        problems.append('await readiness falsely fulfilled or did not reject with failure')
    if not state['renderError']:
        problems.append('bootstrap catch did not publish its declared body.dataset.renderError')
    return problems
