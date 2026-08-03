"""
ArbOS™
EX-061
Execution Transition Guard

Independently validates proposed execution-state transitions
without mutating EX-031 ExecutionStateMachine.
"""


class ExecutionTransitionGuard:
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

    TERMINAL_STATES = {"CLOSED"}

    def evaluate(self, current_state, target_state):
        if current_state is None:
            raise ValueError("unsupported current_state")

        if target_state is None:
            raise ValueError("unsupported target_state")

        current = str(current_state).strip().upper()
        target = str(target_state).strip().upper()

        if current not in self.VALID_STATES:
            raise ValueError("unsupported current_state")

        if target not in self.VALID_STATES:
            raise ValueError("unsupported target_state")

        if current in self.TERMINAL_STATES:
            return {
                "allowed": False,
                "reason": "TERMINAL_STATE",
                "current_state": current,
                "target_state": target,
            }

        allowed_targets = self.VALID_TRANSITIONS.get(
            current,
            set(),
        )

        if target not in allowed_targets:
            return {
                "allowed": False,
                "reason": "INVALID_STATE_TRANSITION",
                "current_state": current,
                "target_state": target,
            }

        return {
            "allowed": True,
            "reason": None,
            "current_state": current,
            "target_state": target,
        }
