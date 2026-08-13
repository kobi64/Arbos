"""
ArbOS™
EX-210
Dynamic Feed Capacity Controller

Makes conservative feed-capacity decisions from an exchange
profile and the current live-feed health state.

Supports confirmation thresholds to prevent capacity
flapping from transient feed-health changes.

Decision layer only.
Does not create or cancel subscriptions.
Does not submit orders.
"""


class DynamicFeedCapacityController:
    def __init__(
        self,
        profile,
        unhealthy_confirmations=1,
        healthy_confirmations=1,
    ):
        if profile is None:
            raise ValueError(
                "profile is required"
            )

        if unhealthy_confirmations <= 0:
            raise ValueError(
                "unhealthy_confirmations must be positive"
            )

        if healthy_confirmations <= 0:
            raise ValueError(
                "healthy_confirmations must be positive"
            )

        self._profile = profile

        self._batch_size = int(
            profile[
                "max_symbols_per_batch"
            ]
        )

        self._max_capacity = int(
            profile.get(
                "max_total_symbols",
                (
                    self._batch_size
                    * int(
                        profile[
                            "max_batches"
                        ]
                    )
                ),
            )
        )

        if self._batch_size <= 0:
            raise ValueError(
                "max_symbols_per_batch must be positive"
            )

        if self._max_capacity <= 0:
            raise ValueError(
                "max_total_symbols must be positive"
            )

        self._unhealthy_confirmations = int(
            unhealthy_confirmations
        )

        self._healthy_confirmations = int(
            healthy_confirmations
        )

        self._consecutive_unhealthy = 0
        self._consecutive_healthy = 0

    def decide(
        self,
        current_capacity,
        health_snapshot,
    ):
        current_capacity = int(
            current_capacity
        )

        if current_capacity <= 0:
            raise ValueError(
                "current_capacity must be positive"
            )

        if health_snapshot is None:
            raise ValueError(
                "health_snapshot is required"
            )

        unhealthy_count = int(
            health_snapshot.get(
                "unhealthy_symbol_count",
                0,
            )
            or 0
        )

        if unhealthy_count > 0:
            self._consecutive_unhealthy += 1
            self._consecutive_healthy = 0

            confirmed = (
                self._consecutive_unhealthy
                >= self._unhealthy_confirmations
            )

            if confirmed:
                target_capacity = max(
                    self._batch_size,
                    current_capacity
                    - self._batch_size,
                )

                if (
                    target_capacity
                    < current_capacity
                ):
                    action = "scale_down"
                    self._consecutive_unhealthy = 0
                else:
                    action = "hold"
            else:
                target_capacity = (
                    current_capacity
                )
                action = "hold"

        else:
            self._consecutive_healthy += 1
            self._consecutive_unhealthy = 0

            confirmed = (
                self._consecutive_healthy
                >= self._healthy_confirmations
            )

            if confirmed:
                target_capacity = min(
                    self._max_capacity,
                    current_capacity
                    + self._batch_size,
                )

                if (
                    target_capacity
                    > current_capacity
                ):
                    action = "scale_up"
                    self._consecutive_healthy = 0
                else:
                    action = "hold"
            else:
                target_capacity = (
                    current_capacity
                )
                action = "hold"

        capacity_change = (
            target_capacity
            - current_capacity
        )

        return {
            "action": action,
            "current_capacity": (
                current_capacity
            ),
            "target_capacity": (
                target_capacity
            ),
            "capacity_change": (
                capacity_change
            ),
            "batch_size": (
                self._batch_size
            ),
            "max_capacity": (
                self._max_capacity
            ),
            "unhealthy_symbol_count": (
                unhealthy_count
            ),
            "consecutive_unhealthy": (
                self._consecutive_unhealthy
            ),
            "consecutive_healthy": (
                self._consecutive_healthy
            ),
            "unhealthy_confirmations": (
                self._unhealthy_confirmations
            ),
            "healthy_confirmations": (
                self._healthy_confirmations
            ),
            "paper_only": True,
            "live_order_submitted": False,
        }
