"""
ArbOS™
EX-151
Staged Test Trade Package

Builds a controlled validation-trade package from a route that
has already passed staged execution readiness.

This module prepares only. It does not submit live orders.
"""

from exchanges.dynamic_execution_risk_allocation import (
    DynamicExecutionRiskAllocation,
)
from exchanges.trade_preparation import (
    TradePreparation,
)


class StagedTestTradePackage:
    def __init__(self):
        self._allocator = DynamicExecutionRiskAllocation()

    def prepare(
        self,
        readiness_result,
        available_capital,
        reliability,
        risk_level,
        estimated_fees,
        slippage_allowance,
    ):
        if readiness_result is None:
            raise ValueError(
                "readiness_result is required"
            )

        if readiness_result.get(
            "ready_for_staged_execution"
        ) is not True:
            return {
                "prepared": False,
                "reason": "staged_execution_not_ready",
                "manual_approval_required": True,
                "approval_granted": False,
                "live_order_submitted": False,
            }

        route = readiness_result.get("route")

        if route is None:
            return {
                "prepared": False,
                "reason": "route_required",
                "manual_approval_required": True,
                "approval_granted": False,
                "live_order_submitted": False,
            }

        allocation = self._allocator.calculate_allocation(
            capital=float(available_capital),
            reliability=float(reliability),
            risk_level=risk_level,
        )

        test_trade_amount = float(
            allocation["test_trade"]
        )

        route_profit_percent = float(
            route.get(
                "net_profit_percent",
                0.0,
            )
        )

        expected_profit = (
            test_trade_amount
            * route_profit_percent
            / 100.0
        )

        asset = str(
            route.get(
                "coin_asset",
                route.get(
                    "transfer_asset",
                    "",
                ),
            )
        ).strip().upper()

        buy_exchange = str(
            route.get(
                "source_exchange",
                "",
            )
        ).strip()

        sell_exchange = str(
            route.get(
                "destination_exchange",
                "",
            )
        ).strip()

        trade_package = TradePreparation.prepare(
            asset=asset,
            buy_exchange=buy_exchange,
            sell_exchange=sell_exchange,
            trade_amount=test_trade_amount,
            expected_profit=expected_profit,
            estimated_fees=float(estimated_fees),
            slippage_allowance=float(
                slippage_allowance
            ),
        )

        return {
            "prepared": bool(
                trade_package.get("ready")
            ),
            "reason": (
                "test_trade_package_prepared"
                if trade_package.get("ready")
                else trade_package.get(
                    "reason",
                    "trade_preparation_failed",
                )
            ),
            "route_id": route.get("route_id"),
            "route_type": route.get(
                "route_type"
            ),
            "test_trade_amount": test_trade_amount,
            "maximum_trade_amount": allocation.get(
                "maximum_trade"
            ),
            "trade_package": trade_package,
            "manual_approval_required": True,
            "approval_granted": False,
            "live_order_submitted": False,
        }
