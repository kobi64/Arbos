"""
ArbOS™
EX-036
Route Reliability Scoring Engine

Measures historical route quality.

Responsibilities:
- Record route executions
- Calculate success rate
- Calculate average profit
- Calculate average slippage
- Generate reliability score
- Maintain route history
"""

from datetime import datetime, UTC


class RouteReliabilityScoring:

    def __init__(self, route_id: str):
        if not route_id:
            raise ValueError("route_id is required")

        self.route_id = route_id
        self.executions = []

        self._history = [
            {
                "route_id": route_id,
                "status": "created",
                "timestamp": datetime.now(UTC).isoformat(),
            }
        ]

    def record_execution(
        self,
        success: bool,
        profit: float,
        slippage: float,
        duration: float,
    ):

        execution = {
            "success": success,
            "profit": profit,
            "slippage": slippage,
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

    def success_rate(self):

        if not self.executions:
            return 0

        successful = sum(
            1
            for execution in self.executions
            if execution["success"]
        )

        rate = (
            successful / len(self.executions)
        ) * 100

        return round(rate, 2)

    def average_profit(self):

        if not self.executions:
            return 0

        total = sum(
            execution["profit"]
            for execution in self.executions
        )

        return round(
            total / len(self.executions),
            2,
        )

    def average_slippage(self):

        if not self.executions:
            return 0

        total = sum(
            execution["slippage"]
            for execution in self.executions
        )

        return round(
            total / len(self.executions),
            2,
        )

    def reliability_score(self):

        if not self.executions:
            return 0

        success_component = self.success_rate()

        profit_component = min(
            self.average_profit(),
            100,
        )

        slippage_penalty = self.average_slippage()

        score = (
            success_component * 0.7
            + profit_component * 0.3
            - slippage_penalty
        )

        return round(
            max(score, 0),
            2,
        )

    def get_history(self):

        return self._history
