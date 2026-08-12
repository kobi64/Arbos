"""
ArbOS™
EX-207
Live Feed Subscription Rotation Controller

Coordinates feed health, rotation planning, and incremental
subscription updates.

The controller:
- reads unhealthy symbols from the manager
- asks the rotation planner for the next active set
- applies the change only when rotation is required
- preserves and updates overflow state

Paper/public-data infrastructure only.
No authentication.
No transfers.
No live orders.
"""


class LiveFeedSubscriptionRotationController:
    def __init__(
        self,
        manager,
        planner,
        active_symbols,
        overflow_symbols,
    ):
        if manager is None:
            raise ValueError(
                "manager is required"
            )

        if planner is None:
            raise ValueError(
                "planner is required"
            )

        self._manager = manager
        self._planner = planner

        self._active_symbols = self._normalize(
            active_symbols
        )

        if not self._active_symbols:
            raise ValueError(
                "active_symbols are required"
            )

        self._overflow_symbols = self._normalize(
            overflow_symbols
        )

    @property
    def active_symbols(self):
        return list(
            self._active_symbols
        )

    @property
    def overflow_symbols(self):
        return list(
            self._overflow_symbols
        )

    async def rebalance(self):
        health = (
            self._manager
            .health_snapshot()
        )

        unhealthy_symbols = (
            health.get(
                "unhealthy_symbols"
            )
            or []
        )

        plan = self._planner.plan(
            active_symbols=(
                self._active_symbols
            ),
            unhealthy_symbols=(
                unhealthy_symbols
            ),
            overflow_symbols=(
                self._overflow_symbols
            ),
        )

        rotation_required = (
            plan.get(
                "rotation_required"
            )
            is True
        )

        if rotation_required:
            await (
                self._manager
                .apply_symbol_rotation(
                    active_symbols=(
                        plan[
                            "active_symbols"
                        ]
                    )
                )
            )

        self._active_symbols = list(
            plan.get(
                "active_symbols",
                self._active_symbols,
            )
        )

        self._overflow_symbols = list(
            plan.get(
                "overflow_symbols",
                self._overflow_symbols,
            )
        )

        return {
            **plan,
            "rotation_required": (
                rotation_required
            ),
            "active_symbols": list(
                self._active_symbols
            ),
            "overflow_symbols": list(
                self._overflow_symbols
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
