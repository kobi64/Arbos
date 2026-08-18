"""
ArbOS™
EX-162
Simulated Route Result P&L

Converts a completed simulated multi-leg route result into the
existing ArbOS paper-route P&L model.

This module performs accounting only. It does not submit orders.
"""

from exchanges.paper_arbitrage_route_pnl import (
    PaperArbitrageRoutePnL,
)


class SimulatedRouteResultPnL:
    def __init__(self):
        self._pnl = PaperArbitrageRoutePnL()

    def evaluate(
        self,
        completion_record,
        starting_value,
        trading_fees=0.0,
        transfer_fees=0.0,
        other_costs=0.0,
        minimum_profit_percent=0.0,
    ):
        if completion_record is None:
            raise ValueError(
                "completion_record is required"
            )

        if completion_record.get(
            "live_order_submitted"
        ) is True:
            return {
                "evaluated": False,
                "reason": "live_order_already_submitted",
                "live_order_submitted": True,
            }

        if completion_record.get(
            "route_complete"
        ) is not True:
            return {
                "evaluated": False,
                "reason": "completed_route_required",
                "live_order_submitted": False,
            }

        if completion_record.get(
            "completed"
        ) is not True:
            return {
                "evaluated": False,
                "reason": "completed_route_required",
                "live_order_submitted": False,
            }

        if completion_record.get(
            "simulated"
        ) is not True:
            return {
                "evaluated": False,
                "reason": "simulated_route_required",
                "live_order_submitted": False,
            }

        route_id = completion_record.get(
            "route_id"
        )
        approval_id = completion_record.get(
            "approval_id"
        )
        permission_id = completion_record.get(
            "permission_id"
        )

        if (
            not isinstance(route_id, str)
            or not route_id.strip()
            or not isinstance(approval_id, str)
            or not approval_id.strip()
            or not isinstance(permission_id, str)
            or not permission_id.strip()
        ):
            return {
                "evaluated": False,
                "reason": "invalid_completion_identity",
                "live_order_submitted": False,
            }

        route_id = route_id.strip()
        approval_id = approval_id.strip()
        permission_id = permission_id.strip()

        raw_final_output_amount = (
            completion_record.get(
                "final_output_amount"
            )
        )

        if raw_final_output_amount is None:
            return {
                "evaluated": False,
                "reason": "final_output_amount_required",
                "live_order_submitted": False,
            }

        try:
            gross_final_value = float(
                raw_final_output_amount
            )
        except (TypeError, ValueError):
            return {
                "evaluated": False,
                "reason": "final_output_amount_invalid",
                "live_order_submitted": False,
            }

        from math import isfinite

        if (
            not isfinite(gross_final_value)
            or gross_final_value < 0
        ):
            return {
                "evaluated": False,
                "reason": "final_output_amount_invalid",
                "live_order_submitted": False,
            }

        pnl = self._pnl.evaluate(
            starting_value=starting_value,
            gross_final_value=gross_final_value,
            trading_fees=trading_fees,
            transfer_fees=transfer_fees,
            other_costs=other_costs,
            minimum_profit_percent=(
                minimum_profit_percent
            ),
        )

        return {
            "evaluated": True,
            "reason": "simulated_route_pnl_evaluated",
            "route_id": route_id,
            "approval_id": approval_id,
            "permission_id": permission_id,
            "completed_leg_number": (
                completion_record.get(
                    "completed_leg_number"
                )
            ),
            "total_legs": completion_record.get(
                "total_legs"
            ),
            "final_symbol": completion_record.get(
                "final_symbol"
            ),
            "final_side": completion_record.get(
                "final_side"
            ),
            "pnl": pnl,
            "test_trade": True,
            "simulated": True,
            "paper_trade": True,
            "live_order_submitted": False,
        }
