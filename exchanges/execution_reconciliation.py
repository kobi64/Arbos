"""
ArbOS™
EX-034
Execution Reconciliation Engine

Verifies expected execution outcomes against actual results.

Responsibilities:
- Store expected balances
- Store actual balances
- Reconcile settlement
- Calculate realised profit
- Account for fees
- Maintain reconciliation history
"""

from datetime import datetime, UTC


class ExecutionReconciliation:

    def __init__(self, execution_id: str):
        if not execution_id:
            raise ValueError("execution_id is required")

        self.execution_id = execution_id

        self.expected = None
        self.actual = None
        self.fees = 0

        self._history = [
            {
                "execution_id": execution_id,
                "status": "created",
                "timestamp": datetime.now(UTC).isoformat(),
            }
        ]

    def set_expected(
        self,
        starting_balance: float,
        expected_balance: float,
    ):

        self.expected = {
            "starting_balance": starting_balance,
            "expected_balance": expected_balance,
        }

        self._history.append(
            {
                "action": "expected_set",
                **self.expected,
                "timestamp": datetime.now(UTC).isoformat(),
            }
        )

        return self.expected

    def set_actual(
        self,
        final_balance: float,
    ):

        self.actual = {
            "actual_balance": final_balance,
        }

        self._history.append(
            {
                "action": "actual_set",
                **self.actual,
                "timestamp": datetime.now(UTC).isoformat(),
            }
        )

        return self.actual

    def reconcile(self):

        if self.expected is None or self.actual is None:
            raise ValueError("missing reconciliation data")

        if self.actual["actual_balance"] == self.expected["expected_balance"]:
            status = "settled"
        else:
            status = "difference"

        result = {
            "execution_id": self.execution_id,
            "status": status,
            "expected": self.expected["expected_balance"],
            "actual": self.actual["actual_balance"],
        }

        self._history.append(
            {
                "action": "reconciled",
                **result,
                "timestamp": datetime.now(UTC).isoformat(),
            }
        )

        return result

    def calculate_profit(self):

        if self.expected is None or self.actual is None:
            raise ValueError("missing reconciliation data")

        profit = round(
            self.actual["actual_balance"]
            - self.expected["starting_balance"],
            2,
        )

        return {
            "execution_id": self.execution_id,
            "profit": profit,
        }

    def add_fees(self, fees: float):

        self.fees = fees

        if self.expected is None or self.actual is None:
            raise ValueError("missing reconciliation data")

        gross_profit = (
            self.actual["actual_balance"]
            - self.expected["starting_balance"]
        )

        net_profit = round(
            gross_profit - fees,
            2,
        )

        result = {
            "execution_id": self.execution_id,
            "fees": fees,
            "net_profit": net_profit,
        }

        self._history.append(
            {
                "action": "fees_added",
                **result,
                "timestamp": datetime.now(UTC).isoformat(),
            }
        )

        return result

    def get_history(self):
        return self._history
