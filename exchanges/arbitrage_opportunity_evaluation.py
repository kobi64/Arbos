"""
ArbOS™
EX-014
Arbitrage Opportunity Evaluation

Combines route feasibility with profitability evaluation
to determine whether an arbitrage opportunity is executable.
"""

from dataclasses import dataclass

from exchanges.arbitrage_profit_evaluation import (
    ArbitrageProfitEvaluation,
)


@dataclass
class ArbitrageOpportunityEvaluationResult:
    valid: bool
    executable: bool = False
    net_profit: float = 0.0
    profit_percent: float = 0.0
    reason: str = ""


class ArbitrageOpportunityEvaluation:

    @staticmethod
    def evaluate(
        route_feasible: bool,
        starting_value: float,
        final_value: float,
        minimum_profit_percent: float,
    ) -> ArbitrageOpportunityEvaluationResult:

        if starting_value <= 0:
            return ArbitrageOpportunityEvaluationResult(
                valid=False,
                executable=False,
                reason="invalid_starting_value",
            )

        if final_value < 0:
            return ArbitrageOpportunityEvaluationResult(
                valid=False,
                executable=False,
                reason="invalid_final_value",
            )

        if minimum_profit_percent < 0:
            return ArbitrageOpportunityEvaluationResult(
                valid=False,
                executable=False,
                reason="invalid_minimum_profit_percent",
            )

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
