"""
ArbOS™
EX-209
Verified Production Feed Profiles

Registers source-backed production feed profiles.

Separates:
- documented exchange capacity / WebSocket limits
- conservative ArbOS™ operating policy

Initial verified exchanges:
- KuCoin
- Bitget

Configuration only.
No authentication.
No transfers.
No live orders.
"""


class VerifiedProductionFeedProfiles:
    VERIFIED_DATE = "2026-08-12"

    def register_all(
        self,
        registry,
    ):
        if registry is None:
            raise ValueError(
                "registry is required"
            )

        profiles = [
            self.kucoin(),
            self.bitget(),
            self.gate(),
            self.digifinex(),
            self.htx(),
            self.xt(),
        ]

        registered = []

        for profile in profiles:
            registry.register(
                profile
            )

            registered.append(
                profile["exchange_id"]
            )

        return {
            "registered_count": len(
                registered
            ),
            "exchange_ids": registered,
            "paper_only": True,
            "live_order_submitted": False,
        }

    def kucoin(
        self,
    ):
        return {
            "exchange_id": "kucoin",

            # ArbOS™ conservative operating policy.
            "max_symbols_per_batch": 80,
            "max_batches": 4,

            "retry_base_delay_seconds": 1.0,
            "retry_max_delay_seconds": 30.0,
            "heartbeat_timeout_seconds": 30.0,
            "max_latency_ms": 1000.0,

            # Exchange-documented capacity.
            "verified_capacity": {
                "max_topics_per_connection": 400,
                "max_topics_per_request": 100,
                "client_messages_per_window": 100,
                "client_message_window_seconds": 10,
            },

            "operating_policy": {
                "policy_owner": "ArbOS",
                "conservative_capacity": True,
                "selected_symbols_per_connection": 320,
            },

            "provenance": {
                "source_type": (
                    "official_exchange_documentation"
                ),
                "verified": True,
                "verified_date": (
                    self.VERIFIED_DATE
                ),
            },
        }

    def bitget(
        self,
    ):
        return {
            "exchange_id": "bitget",

            # ArbOS™ conservative operating policy.
            "max_symbols_per_batch": 40,
            "max_batches": 5,

            "retry_base_delay_seconds": 1.0,
            "retry_max_delay_seconds": 30.0,
            "heartbeat_timeout_seconds": 30.0,
            "max_latency_ms": 1000.0,

            # Exchange-documented capacity.
            "verified_capacity": {
                "max_channels_per_connection": 1000,
                (
                    "recommended_channels_per_connection"
                    "_less_than"
                ): 50,
                "max_connections_per_ip": 100,
                "client_messages_per_second": 10,
            },

            "operating_policy": {
                "policy_owner": "ArbOS",
                "conservative_capacity": True,
                "selected_symbols_per_connection": 200,
            },

            "provenance": {
                "source_type": (
                    "official_exchange_documentation"
                ),
                "verified": True,
                "verified_date": (
                    self.VERIFIED_DATE
                ),
            },
        }

    def gate(
        self,
    ):
        return {
            "exchange_id": "gate",

            # ArbOS™ conservative operating policy.
            "max_symbols_per_batch": 50,
            "max_batches": 4,

            "retry_base_delay_seconds": 1.0,
            "retry_max_delay_seconds": 30.0,
            "heartbeat_timeout_seconds": 30.0,
            "max_latency_ms": 1000.0,

            "verified_capacity": {
                "max_connections_per_ip": 300,
                "documented_symbol_limit": None,
            },

            "operating_policy": {
                "policy_owner": "ArbOS",
                "conservative_capacity": True,
                "capacity_source": (
                    "ArbOS_conservative_policy"
                ),
                "selected_symbols_per_connection": 200,
            },

            "provenance": {
                "source_type": (
                    "official_exchange_documentation"
                ),
                "verified": True,
                "verified_date": (
                    self.VERIFIED_DATE
                ),
            },
        }

    def digifinex(
        self,
    ):
        return {
            "exchange_id": "digifinex",

            # ArbOS™ conservative operating policy.
            "max_symbols_per_batch": 40,
            "max_batches": 4,

            "retry_base_delay_seconds": 1.0,
            "retry_max_delay_seconds": 30.0,
            "heartbeat_timeout_seconds": 30.0,
            "max_latency_ms": 1000.0,

            "verified_capacity": {
                "multi_symbol_subscription_supported": True,
                "documented_symbol_limit": None,
            },

            "operating_policy": {
                "policy_owner": "ArbOS",
                "conservative_capacity": True,
                "capacity_source": (
                    "ArbOS_conservative_policy"
                ),
                "selected_symbols_per_connection": 160,
            },

            "provenance": {
                "source_type": (
                    "official_exchange_documentation"
                ),
                "verified": True,
                "verified_date": (
                    self.VERIFIED_DATE
                ),
            },
        }

    def htx(
        self,
    ):
        return {
            "exchange_id": "htx",

            # ArbOS™ conservative operating policy.
            "max_symbols_per_batch": 40,
            "max_batches": 4,

            "retry_base_delay_seconds": 1.0,
            "retry_max_delay_seconds": 30.0,
            "heartbeat_timeout_seconds": 30.0,
            "max_latency_ms": 1000.0,

            "verified_capacity": {
                "documented_symbol_limit": None,
                "server_ping_interval_seconds": 5,
            },

            "operating_policy": {
                "policy_owner": "ArbOS",
                "conservative_capacity": True,
                "capacity_source": (
                    "ArbOS_conservative_policy"
                ),
                "selected_symbols_per_connection": 160,
            },

            "provenance": {
                "source_type": (
                    "official_exchange_documentation"
                ),
                "verified": True,
                "verified_date": (
                    self.VERIFIED_DATE
                ),
            },
        }

    def xt(
        self,
    ):
        return {
            "exchange_id": "xt",

            # ArbOS™ conservative operating policy.
            "max_symbols_per_batch": 10,
            "max_batches": 8,

            "retry_base_delay_seconds": 1.0,
            "retry_max_delay_seconds": 30.0,
            "heartbeat_timeout_seconds": 60.0,
            "max_latency_ms": 1000.0,

            "verified_capacity": {
                (
                    "max_pairs_per_multi_depth_subscription"
                ): 10,
                (
                    "heartbeat_disconnect_seconds_approx"
                ): 60,
            },

            "operating_policy": {
                "policy_owner": "ArbOS",
                "conservative_capacity": True,
                "capacity_source": (
                    "ArbOS_conservative_policy"
                ),
                "selected_symbols_per_connection": 80,
            },

            "provenance": {
                "source_type": (
                    "official_exchange_documentation"
                ),
                "verified": True,
                "verified_date": (
                    self.VERIFIED_DATE
                ),
            },
        }

