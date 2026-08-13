"""
ArbOS™
EX-210
Dynamic Feed Capacity Orchestrator

Coordinates dynamic feed-capacity decisions and applies
resulting active-symbol changes to the running feed manager.

Flow:
- read live feed health
- decide target capacity
- build active / overflow symbol plan
- apply incremental symbol rotation only when changed
- persist updated active / overflow state

Paper/public-data infrastructure only.
No authentication.
No transfers.
No live orders.
"""


class DynamicFeedCapacityOrchestrator:
    def __init__(
        self,
        manager,
        capacity_controller,
        application_planner,
        active_symbols,
        overflow_symbols,
    ):
        if manager is None:
            raise ValueError(
                "manager is required"
            )

        if capacity_controller is None:
            raise ValueError(
                "capacity_controller is required"
            )

        if application_planner is None:
            raise ValueError(
                "application_planner is required"
            )

        self._manager = manager
        self._capacity_controller = (
            capacity_controller
        )
        self._application_planner = (
            application_planner
        )

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
        health_snapshot = (
            self._manager
            .health_snapshot()
        )

        current_capacity = len(
            self._active_symbols
        )

        decision = (
            self._capacity_controller
            .decide(
                current_capacity=(
                    current_capacity
                ),
                health_snapshot=(
                    health_snapshot
                ),
            )
        )

        target_capacity = int(
            decision.get(
                "target_capacity",
                current_capacity,
            )
        )

        plan = (
            self._application_planner
            .plan(
                active_symbols=(
                    self._active_symbols
                ),
                overflow_symbols=(
                    self._overflow_symbols
                ),
                target_capacity=(
                    target_capacity
                ),
            )
        )

        changed = (
            plan.get(
                "changed"
            )
            is True
        )

        if changed:
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
            **decision,
            **plan,
            "action": plan.get(
                "action",
                decision.get(
                    "action",
                    "hold",
                ),
            ),
            "changed": changed,
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
