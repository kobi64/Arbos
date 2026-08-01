"""
ArbOS™
EX-012
Arbitrage Cost Analysis

Combines buy-side trading fees, transfer costs, and
sell-side trading fees into a single cost evaluation.
"""

from dataclasses import dataclass


@dataclass
class ArbitrageCostAnalysisResult:
    valid: bool
    buy_fee: float = 0.0
    transfer_fee: float = 0.0
    sell_fee: float = 0.0
    total_cost: float = 0.0
    final_value: float = 0.0
    reason: str = ""


class ArbitrageCostAnalysis:

    @staticmethod
    def evaluate(
        starting_value: float,
        buy_fee_percent: float,
        transfer_fee: float,
        sell_fee_percent: float,
    ) -> ArbitrageCostAnalysisResult:

        if starting_value <= 0:
            return ArbitrageCostAnalysisResult(
                valid=False,
                reason="invalid_starting_value",
            )

        if buy_fee_percent < 0:
            return ArbitrageCostAnalysisResult(
                valid=False,
                reason="invalid_buy_fee_percent",
            )

        if sell_fee_percent < 0:
            return ArbitrageCostAnalysisResult(
                valid=False,
                reason="invalid_sell_fee_percent",
            )

        if transfer_fee < 0:
            return ArbitrageCostAnalysisResult(
                valid=False,
                reason="invalid_transfer_fee",
            )

        buy_fee = starting_value * (
            buy_fee_percent / 100
        )

        value_after_buy = starting_value - buy_fee
        value_after_transfer = value_after_buy - transfer_fee

        if value_after_transfer <= 0:
            return ArbitrageCostAnalysisResult(
                valid=False,
                buy_fee=buy_fee,
                transfer_fee=transfer_fee,
                total_cost=buy_fee + transfer_fee,
                final_value=0.0,
                reason="costs_consume_value",
            )

        sell_fee = value_after_transfer * (
            sell_fee_percent / 100
        )

        final_value = value_after_transfer - sell_fee
        total_cost = buy_fee + transfer_fee + sell_fee

        if final_value <= 0:
            return ArbitrageCostAnalysisResult(
                valid=False,
                buy_fee=buy_fee,
                transfer_fee=transfer_fee,
                sell_fee=sell_fee,
                total_cost=total_cost,
                final_value=0.0,
                reason="costs_consume_value",
            )

        return ArbitrageCostAnalysisResult(
            valid=True,
            buy_fee=buy_fee,
            transfer_fee=transfer_fee,
            sell_fee=sell_fee,
            total_cost=total_cost,
            final_value=final_value,
            reason="ok",
        )
