"""
ArbOS™
EX-035
Execution Performance Analytics

Measures completed execution performance.

Responsibilities:
- Record execution outcomes
- Track profit metrics
- Calculate success rate
- Measure slippage
- Score execution routes
- Maintain analytics history
"""

from datetime import datetime, UTC


class ExecutionPerformanceAnalytics:

    def __init__(self, execution_id: str):
        if not execution_id:
            raise ValueError("execution_id is required")

        self.execution_id = execution_id
        self.executions = []
        self.slippage_records = []

        self._history = [
            {
                "execution_id": execution_id,
                "status": "created",
                "timestamp": datetime.now(UTC).isoformat(),
            }
        ]

    def record_execution(
        self,
        status: str,
        profit: float,
        duration: float,
    ):

        execution = {
            "status": status,
            "profit": profit,
            "duration": duration,
        }

        self.executions.append(execution)

        self._history.append(
            {
                "action": "execution_recorded",
                **execution,
                "timestamp": datetime.now(UTC).isoformat(),
            }
        )

        return execution

    def average_profit(self):

        if not self.executions:
            return 0

        total = sum(
            execution["profit"]
            for execution in self.executions
        )

        return total / len(self.executions)

    def success_rate(self):

        if not self.executions:
            return 0

        successful = sum(
            1
            for execution in self.executions
            if execution["status"] == "success"
        )

        return (successful / len(self.executions)) * 100

    def record_slippage(
        self,
        expected_profit: float,
        actual_profit: float,
    ):

        slippage = round(
            expected_profit - actual_profit,
            2,
        )

        record = {
            "expected_profit": expected_profit,
            "actual_profit": actual_profit,
            "slippage": slippage,
        }

        self.slippage_records.append(record)

        self._history.append(
            {
                "action": "slippage_recorded",
                **record,
                "timestamp": datetime.now(UTC).isoformat(),
            }
        )

        return record

    def route_score(self):

        if not self.executions:
            return 0

        profit_score = self.average_profit()
        success_score = self.success_rate() / 100

        return round(
            profit_score * success_score,
            2,
        )

    def get_history(self):

        return self._history
