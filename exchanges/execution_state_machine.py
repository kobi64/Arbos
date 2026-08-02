"""
ArbOS™
EX-031
Execution State Machine

Controls execution lifecycle states.

Responsibilities:
- Maintain execution state
- Validate state transitions
- Record transition history
"""

from datetime import datetime, UTC


class ExecutionStateMachine:

    VALID_STATES = {
        "CREATED",
        "VALIDATED",
        "APPROVED",
        "EXECUTING",
        "COMPLETED",
        "FAILED",
        "RECOVERY",
        "CLOSED",
    }

    VALID_TRANSITIONS = {
        "CREATED": {"VALIDATED"},
        "VALIDATED": {"APPROVED"},
        "APPROVED": {"EXECUTING"},
        "EXECUTING": {"COMPLETED", "FAILED"},
        "FAILED": {"RECOVERY", "CLOSED"},
        "RECOVERY": {"EXECUTING", "CLOSED"},
        "COMPLETED": {"CLOSED"},
        "CLOSED": set(),
    }

    def __init__(self, execution_id: str = "UNKNOWN"):
        self.execution_id = execution_id
        self._state = "CREATED"

        self._history = [
            {
                "execution_id": execution_id,
                "state": "CREATED",
                "timestamp": datetime.now(UTC).isoformat(),
            }
        ]

    def get_state(self):
        return self._state

    def transition(self, new_state: str):

        if new_state not in self.VALID_STATES:
            raise ValueError("invalid state")

        allowed = self.VALID_TRANSITIONS.get(
            self._state,
            set(),
        )

        if new_state not in allowed:
            raise ValueError(
                f"invalid transition {self._state} -> {new_state}"
            )

        self._state = new_state

        record = {
            "execution_id": self.execution_id,
            "state": new_state,
            "timestamp": datetime.now(UTC).isoformat(),
        }

        self._history.append(record)

        return record

    def get_history(self):
        return self._history
