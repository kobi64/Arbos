"""
ArbOS™
EX-047
Execution Failure Recovery Engine

Handles recovery workflow after failed
execution events.
"""

from datetime import datetime, UTC


class ExecutionFailureRecovery:

    def __init__(self):

        self._failures = {}
        self._history = []

    def register_failure(self, transaction_id, reason):

        recovery = {
            "transaction_id": transaction_id,
            "reason": reason,
            "status": "RECOVERY_PENDING",
            "created_at": datetime.now(UTC).isoformat(),
        }

        self._failures[transaction_id] = recovery

        self._history.append(recovery)

        return recovery

    def process_recovery(self, transaction_id):

        if transaction_id not in self._failures:
            return {
                "success": False,
                "reason": "transaction_not_found",
            }

        recovery = self._failures[transaction_id]

        if recovery["status"] == "RECOVERED":
            return {
                "success": False,
                "reason": "recovery_already_completed",
            }

        recovery["status"] = "RECOVERED"
        recovery["updated_at"] = datetime.now(UTC).isoformat()

        return recovery

    def get_history(self):

        return self._history
