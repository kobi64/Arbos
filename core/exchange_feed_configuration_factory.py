"""
ArbOS™
EX-208
Exchange Feed Configuration Factory

Builds exchange-specific live-feed configuration components
from a registered exchange subscription capacity profile.

Composes existing ArbOS™ components only.
No authentication.
No transfers.
No live orders.
"""

from core.exchange_connectivity_supervisor import (
    ExchangeConnectivitySupervisor,
)
from core.live_feed_health_supervisor import (
    LiveFeedHealthSupervisor,
)
from core.live_feed_subscription_batch_planner import (
    LiveFeedSubscriptionBatchPlanner,
)
from core.scanner_health_monitor import (
    ScannerHealthMonitor,
)
from exchanges.order_retry_backoff_policy import (
    OrderRetryBackoffPolicy,
)


class ExchangeFeedConfigurationFactory:
    def __init__(
        self,
        profiles,
    ):
        if profiles is None:
            raise ValueError(
                "profiles is required"
            )

        self._profiles = profiles

    def build(
        self,
        exchange_id,
    ):
        exchange_id = str(
            exchange_id
            or ""
        ).strip().lower()

        if not exchange_id:
            raise ValueError(
                "exchange_id is required"
            )

        profile = self._profiles.get(
            exchange_id
        )

        if profile is None:
            raise ValueError(
                "exchange profile not found"
            )

        batch_planner = (
            LiveFeedSubscriptionBatchPlanner
            .from_profile(
                profile
            )
        )

        scanner_health_monitor = (
            ScannerHealthMonitor(
                heartbeat_timeout_seconds=(
                    profile[
                        "heartbeat_timeout_seconds"
                    ]
                ),
                max_latency_ms=(
                    profile[
                        "max_latency_ms"
                    ]
                ),
            )
        )

        connectivity_supervisor = (
            ExchangeConnectivitySupervisor(
                disconnect_timeout_seconds=(
                    profile[
                        "heartbeat_timeout_seconds"
                    ]
                ),
                max_latency_ms=(
                    profile[
                        "max_latency_ms"
                    ]
                ),
            )
        )

        health_supervisor = (
            LiveFeedHealthSupervisor(
                scanner_health_monitor=(
                    scanner_health_monitor
                ),
                connectivity_supervisor=(
                    connectivity_supervisor
                ),
            )
        )

        backoff_policy = (
            OrderRetryBackoffPolicy(
                base_delay_seconds=(
                    profile[
                        "retry_base_delay_seconds"
                    ]
                ),
                max_delay_seconds=(
                    profile[
                        "retry_max_delay_seconds"
                    ]
                ),
            )
        )

        return {
            "exchange_id": exchange_id,
            "profile": profile,
            "batch_planner": batch_planner,
            "scanner_health_monitor": (
                scanner_health_monitor
            ),
            "connectivity_supervisor": (
                connectivity_supervisor
            ),
            "health_supervisor": (
                health_supervisor
            ),
            "backoff_policy": (
                backoff_policy
            ),
            "paper_only": True,
            "live_order_submitted": False,
        }
