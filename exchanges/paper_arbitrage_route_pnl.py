"""
ArbOS™
EX-072
Paper Arbitrage Route P&L
"""

from exchanges.arbitrage_profit_evaluation import (
    ArbitrageProfitEvaluation,
)


class PaperArbitrageRoutePnL:
    def evaluate(
        self,
        starting_value,
        gross_final_value,
        trading_fees,
        transfer_fees,
        other_costs,
        minimum_profit_percent,
    ):
        if starting_value <= 0:
            raise ValueError("starting_value must be positive")

        if gross_final_value < 0:
            raise ValueError("gross_final_value must be non-negative")

        if minimum_profit_percent < 0:
            raise ValueError("minimum_profit_percent must be non-negative")

        costs = [trading_fees, transfer_fees, other_costs]

        if any(cost < 0 for cost in costs):
            raise ValueError("costs must be non-negative")

        total_costs = trading_fees + transfer_fees + other_costs
        net_final_value = gross_final_value - total_costs

        evaluation = ArbitrageProfitEvaluation.evaluate(
            starting_value=starting_value,
            final_value=net_final_value,
            minimum_profit_percent=minimum_profit_percent,
        )

        return {
            "starting_value": starting_value,
            "gross_final_value": gross_final_value,
            "trading_fees": trading_fees,
            "transfer_fees": transfer_fees,
            "other_costs": other_costs,
            "total_costs": total_costs,
            "net_final_value": net_final_value,
            "net_profit": evaluation.net_profit,
            "profit_percent": evaluation.profit_percent,
            "profitable": evaluation.profitable,
            "reason": evaluation.reason,
        }
