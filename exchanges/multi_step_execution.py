"""
ArbOS™
EX-032
Multi-Step Execution Workflow

Controls multi-stage arbitrage execution.

Responsibilities:
- Track execution steps
- Complete workflow steps
- Handle failures
- Resume failed workflows
- Maintain execution history
"""


from datetime import datetime, UTC


class MultiStepExecution:

    def __init__(
        self,
        execution_id: str,
        steps: list,
    ):
        if not steps:
            raise ValueError("steps required")

        self.execution_id = execution_id
        self.steps = steps
        self.current_index = 0

        self.step_status = {
            step: "pending"
            for step in steps
        }

        self._history = [
            {
                "execution_id": execution_id,
                "status": "created",
                "timestamp": datetime.now(UTC).isoformat(),
            }
        ]

    def get_current_step(self):
        if self.current_index >= len(self.steps):
            return None

        return self.steps[self.current_index]

    def complete_step(self):

        if self.current_index >= len(self.steps):
            return {
                "status": "workflow_completed"
            }

        step = self.steps[self.current_index]

        self.step_status[step] = "completed"

        record = {
            "execution_id": self.execution_id,
            "step": step,
            "status": "completed",
            "timestamp": datetime.now(UTC).isoformat(),
        }

        self._history.append(record)

        self.current_index += 1

        if self.current_index >= len(self.steps):
            return {
                "status": "workflow_completed",
                "step": step,
            }

        return record

    def fail_step(self, reason):

        step = self.get_current_step()

        self.step_status[step] = "failed"

        record = {
            "execution_id": self.execution_id,
            "step": step,
            "status": "failed",
            "reason": reason,
            "timestamp": datetime.now(UTC).isoformat(),
        }

        self._history.append(record)

        return record

    def resume(self):

        step = self.get_current_step()

        self.step_status[step] = "pending"

        record = {
            "execution_id": self.execution_id,
            "step": step,
            "status": "resumed",
            "timestamp": datetime.now(UTC).isoformat(),
        }

        self._history.append(record)

        return record

    def get_history(self):
        return self._history
