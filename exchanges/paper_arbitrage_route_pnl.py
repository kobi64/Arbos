"""
ArbOS™
EX-072
Paper Arbitrage Route P&L
"""

import math

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
        try:
            starting_value = float(starting_value)
        except (TypeError, ValueError):
            raise ValueError("starting_value must be positive")

        if not math.isfinite(starting_value) or starting_value <= 0:
            raise ValueError("starting_value must be positive")

        try:
            gross_final_value = float(gross_final_value)
        except (TypeError, ValueError):
            raise ValueError(
                "gross_final_value must be non-negative"
            )

        if (
            not math.isfinite(gross_final_value)
            or gross_final_value < 0
        ):
            raise ValueError(
                "gross_final_value must be non-negative"
            )

        try:
            minimum_profit_percent = float(
                minimum_profit_percent
            )
        except (TypeError, ValueError):
            raise ValueError(
                "minimum_profit_percent must be non-negative"
            )

        if (
            not math.isfinite(minimum_profit_percent)
            or minimum_profit_percent < 0
        ):
            raise ValueError(
                "minimum_profit_percent must be non-negative"
            )

        raw_costs = [
            trading_fees,
            transfer_fees,
            other_costs,
        ]

        try:
            costs = [float(cost) for cost in raw_costs]
        except (TypeError, ValueError):
            raise ValueError("costs must be non-negative")

        if any(
            not math.isfinite(cost) or cost < 0
            for cost in costs
        ):
            raise ValueError("costs must be non-negative")

        trading_fees, transfer_fees, other_costs = costs

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
