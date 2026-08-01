"""
ArbOS™
EX-011
Trade Cost Analysis

Calculates exchange trading fees and the resulting net
trade value after fees.
"""

from dataclasses import dataclass


@dataclass
class TradeCostAnalysisResult:
    valid: bool
    fee_amount: float = 0.0
    net_value: float = 0.0
    reason: str = ""


class TradeCostAnalysis:

    @staticmethod
    def evaluate(
        trade_value: float,
        fee_percent: float,
    ) -> TradeCostAnalysisResult:

        if trade_value <= 0:
            return TradeCostAnalysisResult(
                valid=False,
                reason="invalid_trade_value",
            )

        if fee_percent < 0:
            return TradeCostAnalysisResult(
                valid=False,
                reason="invalid_fee_percent",
            )

        fee_amount = trade_value * (
            fee_percent / 100
        )

        net_value = trade_value - fee_amount

        if net_value <= 0:
            return TradeCostAnalysisResult(
                valid=False,
                fee_amount=fee_amount,
                net_value=0.0,
                reason="fee_consumes_trade_value",
            )

        return TradeCostAnalysisResult(
            valid=True,
            fee_amount=fee_amount,
            net_value=net_value,
            reason="ok",
        )
