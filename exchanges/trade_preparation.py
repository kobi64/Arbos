"""
ArbOS™
EX-022
Trade Preparation Engine

Creates an execution-ready trade package after all validation gates pass.

Responsibilities:
- Build trade plan
- Calculate net expected profit
- Preserve route information
- Generate approval summary
"""

import math


class TradePreparation:

    @staticmethod
    def prepare(
        asset: str,
        buy_exchange: str,
        sell_exchange: str,
        trade_amount: float,
        expected_profit: float,
        estimated_fees: float,
        slippage_allowance: float,
    ):
        if not isinstance(asset, str) or not asset.strip():
            raise ValueError("asset is required")

        if not isinstance(buy_exchange, str) or not buy_exchange.strip():
            raise ValueError("buy exchange is required")

        if not isinstance(sell_exchange, str) or not sell_exchange.strip():
            raise ValueError("sell exchange is required")

        if isinstance(trade_amount, bool):
            return {
                "ready": False,
                "reason": "invalid_trade_amount",
            }

        try:
            trade_amount = float(trade_amount)
        except (TypeError, ValueError, OverflowError):
            return {
                "ready": False,
                "reason": "invalid_trade_amount",
            }

        if (
            not math.isfinite(trade_amount)
            or trade_amount <= 0
        ):
            return {
                "ready": False,
                "reason": "invalid_trade_amount",
            }

        if isinstance(expected_profit, bool):
            raise ValueError(
                "expected profit must be a finite non-negative number"
            )

        try:
            expected_profit = float(expected_profit)
        except (TypeError, ValueError, OverflowError):
            raise ValueError(
                "expected profit must be a finite non-negative number"
            )

        if (
            not math.isfinite(expected_profit)
            or expected_profit < 0
        ):
            raise ValueError(
                "expected profit must be a finite non-negative number"
            )

        if isinstance(estimated_fees, bool):
            raise ValueError(
                "fees must be a finite non-negative number"
            )

        try:
            estimated_fees = float(estimated_fees)
        except (TypeError, ValueError, OverflowError):
            raise ValueError(
                "fees must be a finite non-negative number"
            )

        if (
            not math.isfinite(estimated_fees)
            or estimated_fees < 0
        ):
            raise ValueError(
                "fees must be a finite non-negative number"
            )

        if isinstance(slippage_allowance, bool):
            raise ValueError(
                "slippage allowance must be a finite non-negative number"
            )

        try:
            slippage_allowance = float(
                slippage_allowance
            )
        except (TypeError, ValueError, OverflowError):
            raise ValueError(
                "slippage allowance must be a finite non-negative number"
            )

        if (
            not math.isfinite(slippage_allowance)
            or slippage_allowance < 0
        ):
            raise ValueError(
                "slippage allowance must be a finite non-negative number"
            )

        net_profit = (
            expected_profit
            - estimated_fees
            - slippage_allowance
        )

        trade = {
            "asset": asset,
            "buy_exchange": buy_exchange,
            "sell_exchange": sell_exchange,
            "trade_amount": trade_amount,
            "expected_profit": expected_profit,
            "estimated_fees": estimated_fees,
            "slippage_allowance": slippage_allowance,
            "net_profit": net_profit,
        }

        return {
            "ready": True,
            "trade": trade,
            "approval_summary": (
                f"Trade {asset}: "
                f"Buy {buy_exchange} → "
                f"Sell {sell_exchange} | "
                f"Net profit: {net_profit}"
            ),
        }
