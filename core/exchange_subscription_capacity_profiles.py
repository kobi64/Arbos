"""
ArbOS™
EX-208
Exchange Subscription Capacity Profiles

Central registry for exchange-specific live feed capacity,
retry, and health defaults.

Configuration only.
No authentication.
No transfers.
No live orders.
"""

from copy import deepcopy


class ExchangeSubscriptionCapacityProfiles:
    def __init__(self):
        self._profiles = {}

    def register(
        self,
        profile,
    ):
        if profile is None:
            raise ValueError(
                "profile is required"
            )

        exchange_id = str(
            profile.get(
                "exchange_id",
                "",
            )
            or ""
        ).strip().lower()

        if not exchange_id:
            raise ValueError(
                "exchange_id is required"
            )

        if exchange_id in self._profiles:
            raise ValueError(
                "exchange profile already registered"
            )

        max_symbols_per_batch = int(
            profile.get(
                "max_symbols_per_batch",
                0,
            )
            or 0
        )

        if max_symbols_per_batch <= 0:
            raise ValueError(
                "max_symbols_per_batch must be positive"
            )

        max_batches = int(
            profile.get(
                "max_batches",
                0,
            )
            or 0
        )

        if max_batches <= 0:
            raise ValueError(
                "max_batches must be positive"
            )

        retry_base_delay_seconds = float(
            profile.get(
                "retry_base_delay_seconds",
                0.0,
            )
            or 0.0
        )

        if retry_base_delay_seconds < 0:
            raise ValueError(
                "retry_base_delay_seconds cannot be negative"
            )

        retry_max_delay_seconds = float(
            profile.get(
                "retry_max_delay_seconds",
                0.0,
            )
            or 0.0
        )

        if retry_max_delay_seconds < 0:
            raise ValueError(
                "retry_max_delay_seconds cannot be negative"
            )

        heartbeat_timeout_seconds = float(
            profile.get(
                "heartbeat_timeout_seconds",
                0.0,
            )
            or 0.0
        )

        if heartbeat_timeout_seconds < 0:
            raise ValueError(
                "heartbeat_timeout_seconds cannot be negative"
            )

        max_latency_ms = float(
            profile.get(
                "max_latency_ms",
                0.0,
            )
            or 0.0
        )

        if max_latency_ms < 0:
            raise ValueError(
                "max_latency_ms cannot be negative"
            )

        normalized = deepcopy(
            profile
        )

        normalized[
            "exchange_id"
        ] = exchange_id

        normalized[
            "max_symbols_per_batch"
        ] = max_symbols_per_batch

        normalized[
            "max_batches"
        ] = max_batches

        normalized[
            "max_total_symbols"
        ] = (
            max_symbols_per_batch
            * max_batches
        )

        normalized[
            "retry_base_delay_seconds"
        ] = retry_base_delay_seconds

        normalized[
            "retry_max_delay_seconds"
        ] = retry_max_delay_seconds

        normalized[
            "heartbeat_timeout_seconds"
        ] = heartbeat_timeout_seconds

        normalized[
            "max_latency_ms"
        ] = max_latency_ms

        normalized[
            "paper_only"
        ] = True

        normalized[
            "live_order_submitted"
        ] = False

        self._profiles[
            exchange_id
        ] = normalized

        return {
            "registered": True,
            "exchange_id": exchange_id,
            "paper_only": True,
            "live_order_submitted": False,
        }

    def get(
        self,
        exchange_id,
    ):
        exchange_id = str(
            exchange_id
            or ""
        ).strip().lower()

        profile = self._profiles.get(
            exchange_id
        )

        if profile is None:
            return None

        return deepcopy(
            profile
        )

    def profile_count(
        self,
    ):
        return len(
            self._profiles
        )
