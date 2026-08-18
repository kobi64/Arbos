"""
ArbOS™
EX-014
Arbitrage Opportunity Evaluation

Combines route feasibility with profitability evaluation
to determine whether an arbitrage opportunity is executable.
"""

from dataclasses import dataclass
import math
from typing import Optional

from exchanges.arbitrage_profit_evaluation import (
    ArbitrageProfitEvaluation,
)


@dataclass
class ArbitrageOpportunityEvaluationResult:
    valid: bool
    executable: bool = False
    net_profit: Optional[float] = None
    profit_percent: Optional[float] = None
    reason: str = ""


class ArbitrageOpportunityEvaluation:

    @staticmethod
    def evaluate(
        route_feasible: bool,
        starting_value: float,
        final_value: float,
        minimum_profit_percent: float,
    ) -> ArbitrageOpportunityEvaluationResult:

        numeric_fields = (
            (
                "starting_value",
                starting_value,
                "invalid_starting_value",
                False,
            ),
            (
                "final_value",
                final_value,
                "invalid_final_value",
                True,
            ),
            (
                "minimum_profit_percent",
                minimum_profit_percent,
                "invalid_minimum_profit_percent",
                True,
            ),
        )

        normalized = {}

        for name, value, reason, allow_zero in numeric_fields:
            if isinstance(value, bool):
                return ArbitrageOpportunityEvaluationResult(
                    valid=False,
                    executable=False,
                    reason=reason,
                )

            try:
                number = float(value)
            except (TypeError, ValueError, OverflowError):
                return ArbitrageOpportunityEvaluationResult(
                    valid=False,
                    executable=False,
                    reason=reason,
                )

            if (
                not math.isfinite(number)
                or number < 0
                or (not allow_zero and number == 0)
            ):
                return ArbitrageOpportunityEvaluationResult(
                    valid=False,
                    executable=False,
                    reason=reason,
                )

            normalized[name] = number

        starting_value = normalized["starting_value"]
        final_value = normalized["final_value"]
        minimum_profit_percent = normalized[
            "minimum_profit_percent"
        ]

        if not route_feasible:
            return ArbitrageOpportunityEvaluationResult(
                valid=True,
                executable=False,
                reason="route_not_feasible",
            )

        profit = ArbitrageProfitEvaluation.evaluate(
            starting_value=starting_value,
            final_value=final_value,
            minimum_profit_percent=minimum_profit_percent,
        )

        if not profit.valid:
            return ArbitrageOpportunityEvaluationResult(
                valid=False,
                executable=False,
                reason=profit.reason,
            )

        if not profit.profitable:
            return ArbitrageOpportunityEvaluationResult(
                valid=True,
                executable=False,
                net_profit=profit.net_profit,
                profit_percent=profit.profit_percent,
                reason=profit.reason,
            )

        return ArbitrageOpportunityEvaluationResult(
            valid=True,
            executable=True,
            net_profit=profit.net_profit,
            profit_percent=profit.profit_percent,
            reason="ok",
        )
