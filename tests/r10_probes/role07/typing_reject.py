"""Expected mypy RED: typed installed read_prompt returns str, never int."""
from deepviz import read_prompt

wrong_type: int = read_prompt()
