"""
ArbOS™
EX-048
Execution Reporting Engine

Creates audit reports for completed
and failed executions.
"""

from datetime import datetime, UTC


class ExecutionReportingEngine:

    def __init__(self):

        self._reports = []

    def create_report(
        self,
        transaction_id,
        expected_value,
        actual_value,
        expected_profit=None
    ):

        if expected_value is None or actual_value is None:
            return {
                "success": False,
                "reason": "missing_execution_data",
            }

        profit = actual_value - expected_value

        report = {
            "transaction_id": transaction_id,
            "expected_value": expected_value,
            "actual_value": actual_value,
            "profit": profit,
            "created_at": datetime.now(UTC).isoformat(),
        }

        if expected_profit is not None:
            report["variance"] = profit - expected_profit

        self._reports.append(report)

        return report

    def create_failure_report(
        self,
        transaction_id,
        reason
    ):

        report = {
            "transaction_id": transaction_id,
            "status": "FAILED",
            "reason": reason,
            "created_at": datetime.now(UTC).isoformat(),
        }

        self._reports.append(report)

        return report

    def get_history(self):

        return self._reports
