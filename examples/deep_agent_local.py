"""Run the real Deep Agents tool graph with a deterministic model, not an LLM.

This checks attachment and tool-result plumbing without credentials or network.
Use deep_agent.py --model provider:model-name for a separately configured live LLM.
"""
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

from deepagents import create_deep_agent
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, ToolMessage
from langchain_core.outputs import ChatGeneration, ChatResult

from deepviz import create_tools


class LocalToolModel(BaseChatModel):
    """Script only the decisions; the graph and all three tools execute normally."""

    @property
    def _llm_type(self) -> str:
        return "deterministic-local-model"

    def bind_tools(self, tools, **kwargs):
        return self

    def _generate(self, messages, stop=None, run_manager=None, **kwargs):
        previous = [message for message in messages if isinstance(message, ToolMessage)]
        if previous and previous[-1].status != "success":
            raise RuntimeError(str(previous[-1].content))
        if previous and previous[-1].name == "render_matplotlib":
            message = AIMessage(content="Static chart ready; inspect its returned metadata and image.")
        else:
            if not previous:
                name, args = "normalize_data", {"data": {"file": "sales.csv"}}
            else:
                result = json.loads(previous[-1].content)
                reference = {"dataset_id": result["dataset_id"]}
                if previous[-1].name == "normalize_data":
                    name, args = "recommend_chart", {"data": reference, "goal": "comparison"}
                else:
                    # Recommendations are editable; known fields/units remain caller decisions.
                    spec = {**result["spec"], "x": "month", "y": "revenue",
                            "title": "Monthly revenue (USD)", "aggregation": "sum"}
                    name, args = "render_matplotlib", {"data": reference, "spec": spec}
            message = AIMessage(content="", tool_calls=[{
                "name": name, "args": args, "id": f"chart-{len(previous)}",
            }])
        return ChatResult(generations=[ChatGeneration(message=message)])


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", default="artifacts/local/deep-agent-local")
    args = parser.parse_args()
    # This checkout example deliberately loads the authoritative source policy.
    policy = (Path(__file__).resolve().parents[1] / "prompts/v1/system.md").read_text(encoding="utf-8")
    with tempfile.TemporaryDirectory(prefix="deepviz-local-input-") as data_dir:
        (Path(data_dir) / "sales.csv").write_text("month,revenue\nJan,12\nFeb,18\nMar,15\n", encoding="utf-8")
        agent = create_deep_agent(
            model=LocalToolModel(), tools=create_tools(args.output_dir, data_dir=data_dir), system_prompt=policy,
        )
        result = agent.invoke({"messages": [{"role": "user", "content": "Compare monthly revenue in USD."}]})
    calls = [message for message in result["messages"] if isinstance(message, ToolMessage)]
    if [message.name for message in calls] != ["normalize_data", "recommend_chart", "render_matplotlib"]:
        raise RuntimeError("Expected the complete profile/recommend/render chain")
    print(json.dumps({"mode": "deterministic-local-model", "tools_called": [m.name for m in calls],
                      "artifact": json.loads(calls[-1].content)}, indent=2))


if __name__ == "__main__":
    main()
