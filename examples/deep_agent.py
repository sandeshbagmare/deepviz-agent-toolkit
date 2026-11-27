"""Attach the tools to a real Deep Agent; an LLM provider/key is supplied by the user."""
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", required=True, help="Installed LangChain provider:model identifier")
    parser.add_argument("--output-dir", default="artifacts/local/deep-agent")
    parser.add_argument("--policy-file", type=Path, help="Explicit trusted policy file for a source checkout")
    args = parser.parse_args()

    from deepagents import create_deep_agent

    from deepviz import create_tools, read_prompt

    policy = args.policy_file.read_text(encoding="utf-8") if args.policy_file else read_prompt("system")
    with tempfile.TemporaryDirectory(prefix="deepviz-input-") as data_dir:
        (Path(data_dir) / "sales.csv").write_text("month,revenue\nJan,12\nFeb,18\nMar,15\n", encoding="utf-8")
        agent = create_deep_agent(
            model=args.model,
            tools=create_tools(args.output_dir, data_dir=data_dir),
            system_prompt=policy,
        )
        result = agent.invoke({"messages": [{"role": "user", "content": (
            'Compare monthly revenue from {"file":"sales.csv"}. The month field is categorical; '
            "revenue is in USD. Profile and recommend, then render a static bar chart and report warnings."
        )}]})
        print(result["messages"][-1].content)


if __name__ == "__main__":
    main()
