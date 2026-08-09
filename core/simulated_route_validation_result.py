"""
ArbOS™
EX-163
Simulated Route Validation Result

Validates a completed simulated route P&L result using the
existing ArbOS paper-route profitability gate.

This module does not authorize or submit live orders.
"""

from exchanges.paper_route_profitability_gate import (
    PaperRouteProfitabilityGate,
)


class SimulatedRouteValidationResult:
    def __init__(self):
        self._profitability_gate = (
            PaperRouteProfitabilityGate()
        )

    def validate(
        self,
        pnl_record,
    ):
        if pnl_record is None:
            raise ValueError(
                "pnl_record is required"
            )

        if pnl_record.get(
            "live_order_submitted"
        ) is True:
            return {
                "validated": False,
                "accepted": False,
                "reason": "live_order_already_submitted",
                "live_order_submitted": True,
            }

        if pnl_record.get(
            "evaluated"
        ) is not True:
            return {
                "validated": False,
                "accepted": False,
                "reason": "evaluated_pnl_required",
                "live_order_submitted": False,
            }

        if pnl_record.get(
            "simulated"
        ) is not True:
            return {
                "validated": False,
                "accepted": False,
                "reason": "simulated_route_required",
                "live_order_submitted": False,
            }

        if pnl_record.get(
            "test_trade"
        ) is not True:
            return {
                "validated": False,
                "accepted": False,
                "reason": "test_trade_required",
                "live_order_submitted": False,
            }

        pnl = pnl_record.get(
            "pnl"
        )

        if pnl is None:
            raise ValueError(
                "pnl is required"
            )

        gate_result = (
            self._profitability_gate.evaluate(
                pnl
            )
        )

        accepted = bool(
            gate_result["accepted"]
        )

        if accepted:
            reason = (
                "simulated_route_validation_passed"
            )
        else:
            reason = (
                "simulated_route_not_profitable"
            )

        return {
            "validated": True,
            "accepted": accepted,
            "reason": reason,
            "route_id": pnl_record.get(
                "route_id"
            ),
            "approval_id": pnl_record.get(
                "approval_id"
            ),
            "permission_id": pnl_record.get(
                "permission_id"
            ),
            "completed_leg_number": (
                pnl_record.get(
                    "completed_leg_number"
                )
            ),
            "total_legs": pnl_record.get(
                "total_legs"
            ),
            "final_symbol": pnl_record.get(
                "final_symbol"
            ),
            "final_side": pnl_record.get(
                "final_side"
            ),
            "net_profit": gate_result.get(
                "net_profit"
            ),
            "profit_percent": (
                gate_result.get(
                    "profit_percent"
                )
            ),
            "profitability_reason": (
                gate_result.get(
                    "reason"
                )
            ),
            "test_trade": True,
            "simulated": True,
            "paper_trade": True,
            "live_order_submitted": False,
        }
