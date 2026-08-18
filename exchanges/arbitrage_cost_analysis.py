"""
ArbOS™
EX-012
Arbitrage Cost Analysis

Combines buy-side trading fees, transfer costs, and
sell-side trading fees into a single cost evaluation.
"""

from dataclasses import dataclass
import math
from typing import Optional


@dataclass
class ArbitrageCostAnalysisResult:
    valid: bool
    buy_fee: Optional[float] = None
    transfer_fee: Optional[float] = None
    sell_fee: Optional[float] = None
    total_cost: Optional[float] = None
    final_value: Optional[float] = None
    reason: str = ""


class ArbitrageCostAnalysis:

    @staticmethod
    def evaluate(
        starting_value: float,
        buy_fee_percent: float,
        transfer_fee: float,
        sell_fee_percent: float,
    ) -> ArbitrageCostAnalysisResult:

        numeric_fields = (
            (
                "starting_value",
                starting_value,
                "invalid_starting_value",
                False,
            ),
            (
                "buy_fee_percent",
                buy_fee_percent,
                "invalid_buy_fee_percent",
                True,
            ),
            (
                "sell_fee_percent",
                sell_fee_percent,
                "invalid_sell_fee_percent",
                True,
            ),
            (
                "transfer_fee",
                transfer_fee,
                "invalid_transfer_fee",
                True,
            ),
        )

        normalized = {}

        for name, value, reason, allow_zero in numeric_fields:
            if isinstance(value, bool):
                return ArbitrageCostAnalysisResult(
                    valid=False,
                    reason=reason,
                )

            try:
                number = float(value)
            except (TypeError, ValueError, OverflowError):
                return ArbitrageCostAnalysisResult(
                    valid=False,
                    reason=reason,
                )

            if (
                not math.isfinite(number)
                or number < 0
                or (not allow_zero and number == 0)
            ):
                return ArbitrageCostAnalysisResult(
                    valid=False,
                    reason=reason,
                )

            normalized[name] = number

        starting_value = normalized["starting_value"]
        buy_fee_percent = normalized["buy_fee_percent"]
        sell_fee_percent = normalized["sell_fee_percent"]
        transfer_fee = normalized["transfer_fee"]

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
