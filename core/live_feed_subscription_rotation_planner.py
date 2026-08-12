"""
ArbOS™
EX-207
Live Feed Subscription Rotation Planner

Produces a deterministic subscription rotation plan.

Unhealthy active symbols are removed.
Highest-priority overflow symbols are promoted into
the vacated active slots.

Planning only.
No authentication.
No transfers.
No live orders.
"""


class LiveFeedSubscriptionRotationPlanner:
    def plan(
        self,
        active_symbols,
        unhealthy_symbols,
        overflow_symbols,
    ):
        active = self._normalize(
            active_symbols
        )

        if not active:
            raise ValueError(
                "active_symbols are required"
            )

        unhealthy = self._normalize(
            unhealthy_symbols
        )

        overflow = self._normalize(
            overflow_symbols
        )

        active_set = set(
            active
        )

        removed_symbols = [
            symbol
            for symbol in active
            if symbol in unhealthy
        ]

        retained_symbols = [
            symbol
            for symbol in active
            if symbol not in unhealthy
        ]

        slots_available = len(
            removed_symbols
        )

        promoted_symbols = (
            overflow[
                :slots_available
            ]
        )

        remaining_overflow = (
            overflow[
                slots_available:
            ]
        )

        new_active = (
            retained_symbols
            + promoted_symbols
        )

        rotation_required = bool(
            removed_symbols
        )

        return {
            "rotation_required": (
                rotation_required
            ),
            "retained_symbols": (
                retained_symbols
            ),
            "removed_symbols": (
                removed_symbols
            ),
            "promoted_symbols": (
                promoted_symbols
            ),
            "active_symbols": (
                new_active
            ),
            "overflow_symbols": (
                remaining_overflow
            ),
            "active_symbol_count": len(
                new_active
            ),
            "overflow_symbol_count": len(
                remaining_overflow
            ),
            "paper_only": True,
            "live_order_submitted": False,
        }

    @staticmethod
    def _normalize(
        symbols,
    ):
        normalized = []
        seen = set()

        for symbol in symbols or []:
            value = str(
                symbol
                or ""
            ).strip().upper()

            if not value:
                continue

            if value in seen:
                continue

            seen.add(
                value
            )

            normalized.append(
                value
            )

        return normalized
