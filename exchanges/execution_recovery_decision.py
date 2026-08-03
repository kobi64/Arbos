"""
ArbOS™
EX-062
Execution Recovery Decision Engine
"""


class ExecutionRecoveryDecisionEngine:
    SUPPORTED_STATES = {
        "FAILED",
        "UNKNOWN",
        "COMPLETED",
        "CLOSED",
        "RECOVERY",
    }

    def decide(
        self,
        execution_state,
        retry_allowed,
        reconciliation_required,
        cancel_possible,
    ):
        if execution_state is None:
            raise ValueError("unsupported execution_state")

        state = str(execution_state).strip().upper()

        if state not in self.SUPPORTED_STATES:
            raise ValueError("unsupported execution_state")

        if state in {"COMPLETED", "CLOSED"}:
            return {
                "action": "STOP",
                "escalate": False,
            }

        if state == "RECOVERY":
            return {
                "action": "CONTINUE_RECOVERY",
                "escalate": False,
            }

        if state == "UNKNOWN":
            return {
                "action": "RECONCILE",
                "escalate": True,
            }

        if reconciliation_required:
            return {
                "action": "RECONCILE",
                "escalate": False,
            }

        if retry_allowed:
            return {
                "action": "RETRY",
                "escalate": False,
            }

        if cancel_possible:
            return {
                "action": "CANCEL",
                "escalate": False,
            }

        return {
            "action": "ESCALATE",
            "escalate": True,
        }
