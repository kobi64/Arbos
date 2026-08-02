"""
ArbOS™
EX-030
Execution Orchestrator

Coordinates the execution workflow.

Responsibilities:
- Receive approved trades
- Apply execution decision flow
- Record execution history
- Return final execution state
"""


from datetime import datetime, UTC


class ExecutionOrchestrator:

    VALID_RISK_STATES = {
        "approved",
        "rejected",
    }

    def __init__(self):
        self._history = []

    def execute(
        self,
        trade_id: str,
        risk_status: str,
        execution_result: str = "success",
    ):
        if not trade_id:
            raise ValueError("trade_id is required")

        if risk_status not in self.VALID_RISK_STATES:
            raise ValueError("invalid risk status")

        timestamp = datetime.now(UTC).isoformat()

        if risk_status == "rejected":
            record = {
                "timestamp": timestamp,
                "trade_id": trade_id,
                "status": "rejected",
                "reason": "risk_check_failed",
            }

            self._history.append(record)
            return record

        if execution_result == "failed":
            record = {
                "timestamp": timestamp,
                "trade_id": trade_id,
                "status": "failed",
            }

            self._history.append(record)
            return record

        record = {
            "timestamp": timestamp,
            "trade_id": trade_id,
            "status": "completed",
        }

        self._history.append(record)
        return record

    def get_history(self):
        return self._history
