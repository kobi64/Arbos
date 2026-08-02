"""
ArbOS™
EX-046
Execution Monitoring Engine

Monitors execution transaction lifecycle
after submission.
"""


from datetime import datetime, UTC


class ExecutionMonitoringEngine:

    def __init__(self):

        self._transactions = {}
        self._history = []

    def register_transaction(self, transaction_id):

        transaction = {
            "transaction_id": transaction_id,
            "status": "MONITORING",
            "created_at": datetime.now(UTC).isoformat(),
        }

        self._transactions[transaction_id] = transaction

        self._history.append(transaction)

        return transaction

    def update_status(self, transaction_id, status):

        if transaction_id not in self._transactions:
            return {
                "success": False,
                "reason": "transaction_not_found",
            }

        transaction = self._transactions[transaction_id]

        transaction["status"] = status
        transaction["updated_at"] = datetime.now(UTC).isoformat()

        return transaction

    def get_history(self):

        return self._history
