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

        gross_final_value = float(
            completion_record.get(
                "final_output_amount",
                0.0,
            )
        )

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
            "route_id": completion_record.get(
                "route_id"
            ),
            "approval_id": completion_record.get(
                "approval_id"
            ),
            "permission_id": completion_record.get(
                "permission_id"
            ),
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
