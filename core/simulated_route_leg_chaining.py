"""
ArbOS™
EX-160
Simulated Route Leg Chaining

Uses a captured simulated fill to prepare the next leg in a
paper-only arbitrage route.

This module does not submit live exchange orders.
"""


class SimulatedRouteLegChaining:
    def chain(
        self,
        fill_record,
        route,
        completed_leg_number,
        completed_leg_side=None,
    ):
        if fill_record is None:
            raise ValueError(
                "fill_record is required"
            )

        if route is None:
            raise ValueError(
                "route is required"
            )

        if fill_record.get(
            "live_order_submitted"
        ) is True:
            return {
                "ready": False,
                "route_complete": False,
                "reason": "live_order_already_submitted",
                "live_order_submitted": True,
            }

        if fill_record.get(
            "fill_captured"
        ) is not True:
            return {
                "ready": False,
                "route_complete": False,
                "reason": "captured_fill_required",
                "live_order_submitted": False,
            }

        route_id = route.get(
            "route_id"
        )
        fill_route_id = fill_record.get(
            "route_id"
        )

        if (
            not isinstance(route_id, str)
            or not route_id.strip()
            or not isinstance(fill_route_id, str)
            or not fill_route_id.strip()
        ):
            return {
                "ready": False,
                "route_complete": False,
                "reason": "invalid_route_identity",
                "live_order_submitted": False,
            }

        route_id = route_id.strip()
        fill_route_id = fill_route_id.strip()

        if route_id != fill_route_id:
            return {
                "ready": False,
                "route_complete": False,
                "reason": "route_id_mismatch",
                "live_order_submitted": False,
            }

        approval_id = fill_record.get(
            "approval_id"
        )
        permission_id = fill_record.get(
            "permission_id"
        )

        if (
            not isinstance(approval_id, str)
            or not approval_id.strip()
            or not isinstance(permission_id, str)
            or not permission_id.strip()
        ):
            return {
                "ready": False,
                "route_complete": False,
                "reason": "invalid_fill_identity",
                "live_order_submitted": False,
            }

        approval_id = approval_id.strip()
        permission_id = permission_id.strip()

        legs = route.get("legs") or []

        completed_leg_number = int(
            completed_leg_number
        )

        if completed_leg_number >= len(legs):
            return {
                "ready": False,
                "route_complete": True,
                "reason": "simulated_route_complete",
                "route_id": route_id,
                "approval_id": approval_id,
                "permission_id": permission_id,
                "test_trade": True,
                "live_order_submitted": False,
            }

        if completed_leg_side is None:
            completed_leg_side = str(
                legs[
                    completed_leg_number - 1
                ].get(
                    "side",
                    "",
                )
            ).strip().lower()
        else:
            completed_leg_side = str(
                completed_leg_side
            ).strip().lower()

        if completed_leg_side == "sell":
            next_quantity = float(
                fill_record.get(
                    "notional",
                    0.0,
                )
            )
        else:
            next_quantity = float(
                fill_record.get(
                    "filled_quantity",
                    0.0,
                )
            )

        next_leg_number = (
            completed_leg_number + 1
        )

        next_leg = dict(
            legs[
                next_leg_number - 1
            ]
        )

        next_leg["quantity"] = (
            next_quantity
        )

        return {
            "ready": True,
            "route_complete": False,
            "reason": "next_simulated_leg_ready",
            "route_id": route_id,
            "approval_id": approval_id,
            "permission_id": permission_id,
            "completed_leg_number": (
                completed_leg_number
            ),
            "next_leg_number": (
                next_leg_number
            ),
            "next_leg": next_leg,
            "test_trade": True,
            "live_order_submitted": False,
        }
