import logging
from typing import Callable


import dspy
from dspy.predict.react import _fmt_exc

logger = logging.getLogger(__name__)


class ReActTruncated(dspy.ReAct):
    def __init__(self, signature, tools: list[Callable], max_iters=5):
        super().__init__(signature, tools, max_iters)

    def forward(self, **input_args):
        trajectory = {}
        max_iters = input_args.pop("max_iters", self.max_iters)
        for idx in range(max_iters):
            try:
                pred = self._call_with_potential_trajectory_truncation(
                    self.react, trajectory, **input_args
                )
            except ValueError as err:
                logger.warning(
                    f"Ending the trajectory: Agent failed to select a valid tool: {_fmt_exc(err)}"
                )
                break

            # TODO: AttributeError: 'NoneType' object has no attribute 'next_thought' (context exceeded)
            trajectory[f"thought_{idx}"] = pred.next_thought
            trajectory[f"tool_name_{idx}"] = pred.next_tool_name
            trajectory[f"tool_args_{idx}"] = pred.next_tool_args

            print(f"[{idx}] Thought: {pred.next_thought}")
            print(f"[{idx}] Tool: {pred.next_tool_name} | Args: {pred.next_tool_args}")

            try:
                # --------- truncate previous observations (DOM) ---------
                for j in range(idx):
                    try:
                        trajectory[f"observation_{j}"]["new_state"]["snapshot"] = "truncated"
                    except TypeError:
                        pass
                # ---------
                trajectory[f"observation_{idx}"] = self.tools[pred.next_tool_name](
                    **pred.next_tool_args
                )
            except Exception as err:
                trajectory[f"observation_{idx}"] = (
                    f"Execution error in {pred.next_tool_name}: {_fmt_exc(err)}"
                )

            if pred.next_tool_name == "finish":
                break

        extract = self._call_with_potential_trajectory_truncation(
            self.extract, trajectory, **input_args
        )
        return dspy.Prediction(trajectory=trajectory, **extract)
