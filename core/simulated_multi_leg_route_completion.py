"""
ArbOS™
EX-161
Simulated Multi-Leg Route Completion

Validates and records completion of a fully simulated multi-leg
arbitrage route after the final leg fill has been captured.

This module does not submit live exchange orders.
"""

import math


class SimulatedMultiLegRouteCompletion:
    def complete(
        self,
        final_fill,
        route,
        completed_leg_number,
    ):
        if final_fill is None:
            raise ValueError(
                "final_fill is required"
            )

        if route is None:
            raise ValueError(
                "route is required"
            )

        if final_fill.get(
            "live_order_submitted"
        ) is True:
            return {
                "completed": False,
                "route_complete": False,
                "reason": "live_order_already_submitted",
                "live_order_submitted": True,
            }

        if final_fill.get(
            "fill_captured"
        ) is not True:
            return {
                "completed": False,
                "route_complete": False,
                "reason": "captured_fill_required",
                "live_order_submitted": False,
            }

        route_id = route.get(
            "route_id"
        )

        if route_id != final_fill.get(
            "route_id"
        ):
            return {
                "completed": False,
                "route_complete": False,
                "reason": "route_id_mismatch",
                "live_order_submitted": False,
            }

        legs = route.get(
            "legs"
        ) or []

        if not legs:
            return {
                "completed": False,
                "route_complete": False,
                "reason": "route_legs_required",
                "route_id": route_id,
                "live_order_submitted": False,
            }

        completed_leg_number = int(
            completed_leg_number
        )

        total_legs = len(
            legs
        )

        if completed_leg_number != total_legs:
            return {
                "completed": False,
                "route_complete": False,
                "reason": "final_leg_required",
                "route_id": route_id,
                "completed_leg_number": (
                    completed_leg_number
                ),
                "total_legs": total_legs,
                "live_order_submitted": False,
            }

        final_leg = dict(
            legs[-1]
        )

        final_side = str(
            final_leg.get(
                "side",
                "",
            )
        ).strip().lower()

        try:
            filled_quantity = float(
                final_fill["filled_quantity"]
            )
            notional = float(
                final_fill["notional"]
            )
        except (KeyError, TypeError, ValueError):
            return {
                "completed": False,
                "route_complete": False,
                "reason": "invalid_final_fill_values",
                "route_id": route_id,
                "live_order_submitted": False,
            }

        if (
            not math.isfinite(filled_quantity)
            or not math.isfinite(notional)
            or filled_quantity <= 0
            or notional < 0
        ):
            return {
                "completed": False,
                "route_complete": False,
                "reason": "invalid_final_fill_values",
                "route_id": route_id,
                "live_order_submitted": False,
            }

        if final_side == "sell":
            if notional <= 0:
                return {
                    "completed": False,
                    "route_complete": False,
                    "reason": "invalid_final_fill_values",
                    "route_id": route_id,
                    "live_order_submitted": False,
                }

            final_output_amount = notional
        else:
            final_output_amount = filled_quantity

        return {
            "completed": True,
            "route_complete": True,
            "reason": "simulated_multi_leg_route_complete",
            "route_id": route_id,
            "approval_id": final_fill.get(
                "approval_id"
            ),
            "permission_id": final_fill.get(
                "permission_id"
            ),
            "completed_leg_number": (
                completed_leg_number
            ),
            "total_legs": total_legs,
            "final_symbol": final_leg.get(
                "symbol"
            ),
            "final_side": final_side,
            "final_filled_quantity": (
                filled_quantity
            ),
            "final_notional": (
                notional
            ),
            "final_output_amount": (
                final_output_amount
            ),
            "test_trade": True,
            "simulated": True,
            "paper_trade": True,
            "live_order_submitted": False,
        }
