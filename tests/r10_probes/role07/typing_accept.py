"""Positive PEP561 check against the installed consumer interpreter, not checkout paths."""
from deepviz import ChartSpec, NormalizedData, normalize, read_prompt

prompt: str = read_prompt()
spec: ChartSpec = ChartSpec(kind="bar", x="label", y="value")
normalized: NormalizedData = normalize([{"label": "A", "value": 2}], spec)
count: int = normalized.input_count
