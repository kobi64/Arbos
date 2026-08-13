"""
ArbOS™
EX-210
Dynamic Feed Capacity Application Planner

Applies a target feed capacity to active and overflow
symbol sets.

Scale-down:
- retains highest-priority active symbols
- demotes excess active symbols to the front of overflow

Scale-up:
- promotes highest-priority overflow symbols

Planning only.
No authentication.
No transfers.
No live orders.
"""


class DynamicFeedCapacityApplicationPlanner:
    def plan(
        self,
        active_symbols,
        overflow_symbols,
        target_capacity,
    ):
        active = self._normalize(
            active_symbols
        )

        if not active:
            raise ValueError(
                "active_symbols are required"
            )

        overflow = self._normalize(
            overflow_symbols
        )

        target_capacity = int(
            target_capacity
        )

        if target_capacity <= 0:
            raise ValueError(
                "target_capacity must be positive"
            )

        current_capacity = len(
            active
        )

        if target_capacity < current_capacity:
            retained = active[
                :target_capacity
            ]

            demoted = active[
                target_capacity:
            ]

            new_overflow = (
                demoted
                + overflow
            )

            return {
                "action": "scale_down",
                "changed": True,
                "active_symbols": retained,
                "overflow_symbols": (
                    new_overflow
                ),
                "promoted_symbols": [],
                "demoted_symbols": demoted,
                "active_symbol_count": len(
                    retained
                ),
                "overflow_symbol_count": len(
                    new_overflow
                ),
                "target_capacity": (
                    target_capacity
                ),
                "paper_only": True,
                "live_order_submitted": False,
            }

        if target_capacity > current_capacity:
            slots_available = (
                target_capacity
                - current_capacity
            )

            promoted = overflow[
                :slots_available
            ]

            remaining_overflow = overflow[
                slots_available:
            ]

            new_active = (
                active
                + promoted
            )

            return {
                "action": "scale_up",
                "changed": bool(
                    promoted
                ),
                "active_symbols": (
                    new_active
                ),
                "overflow_symbols": (
                    remaining_overflow
                ),
                "promoted_symbols": (
                    promoted
                ),
                "demoted_symbols": [],
                "active_symbol_count": len(
                    new_active
                ),
                "overflow_symbol_count": len(
                    remaining_overflow
                ),
                "target_capacity": (
                    target_capacity
                ),
                "paper_only": True,
                "live_order_submitted": False,
            }

        return {
            "action": "hold",
            "changed": False,
            "active_symbols": active,
            "overflow_symbols": overflow,
            "promoted_symbols": [],
            "demoted_symbols": [],
            "active_symbol_count": len(
                active
            ),
            "overflow_symbol_count": len(
                overflow
            ),
            "target_capacity": (
                target_capacity
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
