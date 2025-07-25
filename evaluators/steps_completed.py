# evaluators/steps_completed.py
# This is an example.
from __future__ import annotations
from typing import List, Set, Union, Optional
from langsmith.evaluation import RunEvaluator, EvaluationResult
from langsmith.schemas import Run, Example

class StepsCompleted(RunEvaluator):
    """
    Calculate the percentage of requested tool steps completed in a run.
    `required_steps` can be hardcoded or retrieved from Example.metadata.
    
    Evaluation metrics:
    - key: "steps_completed" - Metric name
    - score: float (0-1) - Proportion of steps completed
    - value: str - Text description of completion status (format: "completed/total")
    - comment: str - Detailed diagnostic information including completed and missing steps
    """
    def __init__(self, required_steps: List[str]):
        """
        Initialize the StepsCompleted evaluator
        
        Args:
            required_steps: List of required steps that must be completed
        """
        self.required_steps: Set[str] = set(required_steps)

    def evaluate_run(
        self, run: Run, example: Optional[Example] = None
    ) -> Union[EvaluationResult, dict]:
        """
        Evaluate the steps completed in a run
        
        Args:
            run: The run to evaluate
            example: Optional example object
            
        Returns:
            EvaluationResult or dict formatted evaluation result
        """
        try:
            # 1. Collect all successfully executed child nodes (tool calls)
            executed = {child.name for child in run.child_runs
                        if child.status == "success"}
            
            # 2. Calculate completion rate
            total_required = len(self.required_steps)
            
            # Handle special case of empty required steps
            if total_required == 0:
                return EvaluationResult(
                    key="steps_completed",
                    score=1.0,
                    value="No required steps",
                    comment="No required steps specified for evaluation"
                )
            
            completed = len(executed & self.required_steps)
            score = completed / total_required
            
            # 3. Return standardized EvaluationResult object
            return EvaluationResult(
                key="steps_completed",
                score=score,
                value=f"{completed}/{total_required}",
                comment=f"Completed steps: {list(executed & self.required_steps)}, Missing steps: {list(self.required_steps - executed)}"
            )
        except Exception as e:
            # Error handling to ensure evaluator doesn't fail due to exceptions
            return EvaluationResult(
                key="steps_completed",
                score=0.0,
                value="Error",
                comment=f"Error in evaluation: {str(e)}"
            )
