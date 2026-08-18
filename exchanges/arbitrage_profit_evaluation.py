"""
ArbOS™
EX-013
Arbitrage Profit Evaluation

Evaluates final arbitrage profitability after costs by comparing
the ending value against starting capital and a minimum required
profit threshold.
"""

from dataclasses import dataclass
import math
from typing import Optional


@dataclass
class ArbitrageProfitEvaluationResult:
    valid: bool
    profitable: bool = False
    net_profit: Optional[float] = None
    profit_percent: Optional[float] = None
    reason: str = ""


class ArbitrageProfitEvaluation:

    @staticmethod
    def evaluate(
        starting_value: float,
        final_value: float,
        minimum_profit_percent: float,
    ) -> ArbitrageProfitEvaluationResult:

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
                return ArbitrageProfitEvaluationResult(
                    valid=False,
                    reason=reason,
                )

            try:
                number = float(value)
            except (TypeError, ValueError, OverflowError):
                return ArbitrageProfitEvaluationResult(
                    valid=False,
                    reason=reason,
                )

            if (
                not math.isfinite(number)
                or number < 0
                or (not allow_zero and number == 0)
            ):
                return ArbitrageProfitEvaluationResult(
                    valid=False,
                    reason=reason,
                )

            normalized[name] = number

        starting_value = normalized["starting_value"]
        final_value = normalized["final_value"]
        minimum_profit_percent = normalized[
            "minimum_profit_percent"
        ]

        net_profit = final_value - starting_value

        profit_percent = (
            net_profit / starting_value
        ) * 100

        if profit_percent < minimum_profit_percent:
            return ArbitrageProfitEvaluationResult(
                valid=True,
                profitable=False,
                net_profit=net_profit,
                profit_percent=profit_percent,
                reason="below_minimum_profit",
            )

        return ArbitrageProfitEvaluationResult(
            valid=True,
            profitable=True,
            net_profit=net_profit,
            profit_percent=profit_percent,
            reason="ok",
        )
