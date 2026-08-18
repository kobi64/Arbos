"""
ArbOS™
EX-013
Arbitrage Profit Evaluation

Evaluates final arbitrage profitability after costs by comparing
the ending value against starting capital and a minimum required
profit threshold.
"""

from dataclasses import dataclass
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

        if starting_value <= 0:
            return ArbitrageProfitEvaluationResult(
                valid=False,
                reason="invalid_starting_value",
            )

        if final_value < 0:
            return ArbitrageProfitEvaluationResult(
                valid=False,
                reason="invalid_final_value",
            )

        if minimum_profit_percent < 0:
            return ArbitrageProfitEvaluationResult(
                valid=False,
                reason="invalid_minimum_profit_percent",
            )

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
