"""
ArbOS™
EX-064
Execution Control Pipeline
"""

from exchanges.exchange_execution_safety_gate import (
    ExchangeExecutionSafetyGate,
)
from exchanges.execution_audit_trail import ExecutionAuditTrail
from exchanges.execution_transition_guard import (
    ExecutionTransitionGuard,
)


class ExecutionControlPipeline:
    def __init__(self):
        self._safety_gate = ExchangeExecutionSafetyGate()
        self._transition_guard = ExecutionTransitionGuard()
        self._audit = ExecutionAuditTrail()

    @staticmethod
    def _require_execution_id(execution_id):
        if execution_id is None or not str(execution_id).strip():
            raise ValueError("execution_id is required")

        return str(execution_id).strip()

    def evaluate(
        self,
        execution_id,
        context,
        current_state,
        target_state,
    ):
        execution_id = self._require_execution_id(execution_id)

        if context is None:
            raise ValueError("context is required")

        safety_result = self._safety_gate.evaluate(context)

        if not safety_result["allowed"]:
            decision = "SAFETY_BLOCKED"
            reasons = list(safety_result["reasons"])

            self._audit.record(
                execution_id=execution_id,
                event=decision,
                state=current_state,
                metadata={
                    "reasons": reasons,
                    "target_state": target_state,
                },
            )

            return {
                "allowed": False,
                "decision": decision,
                "reasons": reasons,
            }

        transition_result = self._transition_guard.evaluate(
            current_state,
            target_state,
        )

        if not transition_result["allowed"]:
            decision = "TRANSITION_BLOCKED"
            reasons = [transition_result["reason"]]

            self._audit.record(
                execution_id=execution_id,
                event=decision,
                state=current_state,
                metadata={
                    "reasons": reasons,
                    "target_state": target_state,
                },
            )

            return {
                "allowed": False,
                "decision": decision,
                "reasons": reasons,
            }

        decision = "EXECUTION_ALLOWED"

        self._audit.record(
            execution_id=execution_id,
            event=decision,
            state=target_state,
            metadata={
                "reasons": [],
                "previous_state": current_state,
            },
        )

        return {
            "allowed": True,
            "decision": decision,
            "reasons": [],
        }

    def audit_history(self, execution_id):
        return self._audit.history(execution_id)

    def latest_audit(self, execution_id):
        return self._audit.latest(execution_id)
