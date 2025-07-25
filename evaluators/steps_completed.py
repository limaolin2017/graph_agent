# evaluators/steps_completed.py
# This is an example.
from __future__ import annotations
from typing import List, Set
from langsmith.evaluation import RunEvaluator, EvaluationResult
from langsmith.schemas import Run, Example          # Example 可选

class StepsCompleted(RunEvaluator):
    """
    计算 run 内真正完成的工具步骤占用户请求步骤的比例。
    `required_steps` 可以写死，也可以从 Example.metadata 里读取。
    """
    def __init__(self, required_steps: List[str]):
        self.required_steps: Set[str] = set(required_steps)

    def evaluate_run(
        self, run: Run, example: Example | None = None, **_
    ) -> EvaluationResult | dict:
        # 1. 收集所有成功执行的子节点（tool call）
        executed = {child.name for child in run.child_runs
                    if child.status == "success"}
        # 2. 计算命中率
        completed = len(executed & self.required_steps)
        score = completed / len(self.required_steps)
        # 3. 返回数值分数 + 诊断信息
        return {
            "key": "steps_completed",  # 指标名
            "score": score,            # 数值评分 (0‑1)
            "value": f"{completed}/{len(self.required_steps)}",
            "completed": list(executed & self.required_steps),
            "missing": list(self.required_steps - executed),
        }
