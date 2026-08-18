"""
ArbOS™
EX-159
Simulated Test Trade Fill Capture

Captures and normalizes a completed simulated staged test-trade fill.

This module records paper execution results only.
It does not submit live exchange orders.
"""


class SimulatedTestTradeFillCapture:
    def capture(
        self,
        execution_result,
    ):
        if execution_result is None:
            raise ValueError(
                "execution_result is required"
            )

        if execution_result.get(
            "live_order_submitted"
        ) is True:
            return {
                "fill_captured": False,
                "reason": "live_order_already_submitted",
                "live_order_submitted": True,
            }

        if execution_result.get(
            "simulated"
        ) is not True:
            return {
                "fill_captured": False,
                "reason": "simulated_execution_required",
                "live_order_submitted": False,
            }

        if execution_result.get(
            "test_trade"
        ) is not True:
            return {
                "fill_captured": False,
                "reason": "test_trade_required",
                "live_order_submitted": False,
            }

        if execution_result.get(
            "status"
        ) != "FILLED":
            return {
                "fill_captured": False,
                "reason": "simulated_trade_not_filled",
                "live_order_submitted": False,
            }

        import math

        try:
            filled_quantity = float(
                execution_result["filled_quantity"]
            )
            average_price = float(
                execution_result["average_price"]
            )
            notional = float(
                execution_result["notional"]
            )
        except (KeyError, TypeError, ValueError):
            return {
                "fill_captured": False,
                "reason": "invalid_simulated_fill_values",
                "live_order_submitted": False,
            }

        if (
            not math.isfinite(filled_quantity)
            or not math.isfinite(average_price)
            or not math.isfinite(notional)
            or filled_quantity <= 0
            or average_price <= 0
            or notional < 0
        ):
            return {
                "fill_captured": False,
                "reason": "invalid_simulated_fill_values",
                "live_order_submitted": False,
            }

        return {
            "fill_captured": True,
            "reason": "simulated_test_trade_fill_captured",
            "status": "FILLED",
            "simulated": True,
            "paper_trade": bool(
                execution_result.get(
                    "paper_trade",
                    True,
                )
            ),
            "paper_order_id": execution_result.get(
                "paper_order_id"
            ),
            "order_id": execution_result.get(
                "order_id"
            ),
            "route_id": execution_result.get(
                "route_id"
            ),
            "approval_id": execution_result.get(
                "approval_id"
            ),
            "permission_id": execution_result.get(
                "permission_id"
            ),
            "filled_quantity": filled_quantity,
            "average_price": average_price,
            "notional": notional,
            "market_price": execution_result.get(
                "market_price"
            ),
            "test_trade": True,
            "live_order_submitted": False,
        }
