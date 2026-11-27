"""Print a concrete documentation-only proposal; never modify shared documents."""
from __future__ import annotations

import difflib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
REPLACEMENTS = {
    "docs/capabilities.md": [
        (
            "## What the shared model establishes",
            "## Current checkpoint addendum — `3aa521a5`\n\n"
            "The dated baseline tables below remain historical, not a new final-source\n"
            "signoff. Current source and small local controls establish these deltas:\n\n"
            "- Python ECharts now emits the 6.1.0 jsDelivr URL; G2 remains 5.4.8. Writing\n"
            "  HTML did not test CDN availability or browser geometry.\n"
            "- Exercised Python bar paths omit invalid y with warnings across five engines;\n"
            "  output_count still counts normalized rows, not drawn marks. Line/area/radar\n"
            "  gap handling is source-observed, not an all-kind browser certification.\n"
            "- Python has 64 KiB cell / 256 KiB record / 16 MiB retained UTF-8 guards,\n"
            "  1 MiB replay-row / 64 MiB replay-total and 32 MiB combined payload guards.\n"
            "  npm has 64 KiB cell-or-name / 256 KiB record / 16 MiB state / 32 MiB combined\n"
            "  guards; HTML separately uses 20M characters. Python names currently cap at\n"
            "  4 KiB, an unresolved policy/parity difference.\n"
            "  Small reject controls are not exhaustive envelope or process-memory proof.\n"
            "- Direct encoded-JSON duplicate rejection was checked on one small control;\n"
            "  this does not prove every nested carrier or ToolSession string-decoding mode.\n"
            "- Checkout examples ran with explicit source imports, not a clean installation.\n"
            "  Installed prompt availability, live-provider adherence, npm prompt shipping,\n"
            "  all-kind visuals and final acceptance require their separate evidence.\n\n"
            "## What the shared model establishes",
        ),
    ],
    "README.md": [
        ("HTML loads ECharts **5.6.0**", "HTML loads ECharts **6.1.0**"),
        (
            "- Those integration caps are not demonstrated per-cell, retained-UTF-8-byte or\n"
            "  dashboard-spool quotas for Python direct/file rendering. JSON documents can be\n"
            "  read wholesale, strings can be large, and iterator dashboard replay can exhaust\n"
            "  temporary disk. Do not treat planned byte budgets as implemented protections.",
            "- At checkpoint `3aa521a5`, implemented UTF-8 guards reject string cells over\n"
            "  64 KiB, flattened records over 256 KiB, and retained normalized state over\n"
            "  16 MiB. Python dashboard replay is limited to 1 MiB per encoded record and\n"
            "  64 MiB total JSONL; combined retained/spec/native payloads have a 32 MiB guard.\n"
            "  The current Python field-name ceiling is 4 KiB versus npm's 64 KiB; this\n"
            "  implementation difference is not a resolved cross-language policy contract.\n"
            "  JSON parsing may still materialize input; native geometry, images, escaped\n"
            "  HTML, caller-owned objects and runtime overhead are not process-memory quotas.",
        ),
        (
            "- **Current Python correctness limit:** null/non-numeric mapped y values can become\n"
            "  zero in adapter channels without warnings; a wholly absent mapped field is a\n"
            "  different validation case. npm instead rejects invalid numeric chart mappings.\n"
            "  Filter/validate measurements yourself and inspect actual output; the policy\n"
            "  goal of explicit errors/warnings is not proof every current path achieves it.",
            "- **Current Python missing-value behavior:** invalid mapped y measurements are\n"
            "  omitted from ordinary mark geometry with warnings; line/area/radar paths use\n"
            "  warned gaps. A wholly absent mapped field is a different validation case.\n"
            "  `output_count` counts bounded normalized records, not the number of drawn marks.\n"
            "  npm rejects invalid numeric mappings instead. Validate measurements and inspect\n"
            "  the intended engine/kind; the small example checks are not all-kind signoff.",
        ),
    ],
    "examples/README.md": [
        ("ECharts 5.6.0 and G2 5.4.8", "ECharts 6.1.0 and G2 5.4.8"),
    ],
    "prompts/v1/system.md": [
        (
            "- Do not trust the absence of warnings as validation: current Python channels can\n"
            "  turn invalid y into zero. Require cleaned/validated measurements rather than\n"
            "  present a fabricated zero as observed. Plotly heatmap is colored-square scatter,\n"
            "  and Vega gauge ordinary bars; do not promise grid cells or gauge clamping there.",
            "- Require cleaned/validated measurements. Current Python paths omit invalid y\n"
            "  from mark geometry with warnings, or show warned gaps for line/area/radar.\n"
            "  Report omitted values: output_count counts normalized rows, not drawn marks.\n"
            "  An absence of warnings is not all-kind validation. Plotly heatmap remains\n"
            "  colored-square scatter and Vega gauge ordinary bars; do not promise native\n"
            "  grid cells or gauge clamping there.",
        ),
    ],
    "packages/deepviz/README.md": [
        (
            "This is the npm behavior, not proof of Python adapter parity: the separately\n"
            "inspected Python baseline can turn invalid y measurements into zero without a\n"
            "warning. Review [the runtime-specific capability matrix](../../docs/capabilities.md).",
            "This is npm behavior, not proof of Python adapter parity. At checkpoint `3aa521a5`,\n"
            "Python omits invalid y from ordinary mark geometry or uses warned line/area/radar\n"
            "gaps; normalized output_count is not a drawn-mark count. Review the dated\n"
            "[runtime-specific capability matrix](../../docs/capabilities.md) and its addendum.",
        ),
        (
            "Safety budgets: nesting depth 64; 1024 flattened fields per record/schema; text fields\n"
            "truncate at 10000 UTF-16 code units; normalized records have a 100000-character\n"
            "budget, retained normalized data a 16-million-character budget, and HTML a\n"
            "20-million-character budget. Character budgets are not exact heap-byte limits.\n"
            "Output rows and retained group states are bounded independently of input count.\n"
            "JSON strings must still be parsed in memory; true incremental input uses an\n"
            "async source of records/pages, not raw text chunks.\n"
            "These are the implemented **character-based** guards inspected at `b6abc8d`, not\n"
            "proof of newer UTF-8-byte budget policies, a total-process memory cap, a Python\n"
            "spool quota, or a combined dashboard budget. Do not infer encoded JSON duplicate-key\n"
            "rejection from duplicate CSV-header rejection; reject ambiguous repeated JSON keys\n"
            "upstream until the parser contract is independently verified.",
            "At checkpoint `3aa521a5`, safety budgets reject text cells/field names over 64 KiB\n"
            "UTF-8, flattened records over 256 KiB, retained normalized state over 16 MiB,\n"
            "and combined retained/native chart payloads over 32 MiB; text is not silently\n"
            "truncated. Depth 64 and 1,024-field limits also apply. HTML separately has a\n"
            "20-million-character guard, not an exact heap-byte limit. Python's field-name\n"
            "ceiling differs (4 KiB); policy/parity work remains explicit, not assumed solved.\n"
            "JSON text still parses in memory; incremental input uses records/pages, not raw\n"
            "text chunks. Direct encoded-JSON duplicate rejection was checked with one small\n"
            "control; that does not establish every nested/carrier/tool-string path. Runtime,\n"
            "native geometry and escaped-HTML overhead are not process-memory quotas.",
        ),
        (
            "Vega-Lite SVG, and uses ECharts 5.6.0 rather than npm's 6.1.0.",
            "Vega-Lite SVG, and now uses ECharts 6.1.0, the same pin as npm.",
        ),
    ],
}


def proposed_text(relative: str) -> str:
    """Apply exact single-occurrence replacements in memory, preserving old evidence."""
    text = (ROOT / relative).read_text(encoding="utf-8")
    for old, new in REPLACEMENTS[relative]:
        assert text.count(old) == 1, f"Proposal context drifted: {relative}: {old[:50]}"
        text = text.replace(old, new, 1)
    return text


def main() -> None:
    for relative in REPLACEMENTS:
        original = (ROOT / relative).read_text(encoding="utf-8")
        proposed = proposed_text(relative)
        print("".join(difflib.unified_diff(
            original.splitlines(keepends=True), proposed.splitlines(keepends=True),
            fromfile=f"a/{relative}", tofile=f"b/{relative}",
        )), end="")


if __name__ == "__main__":
    main()
