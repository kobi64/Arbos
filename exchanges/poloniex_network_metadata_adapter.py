"""
ArbOS™
EX-218
Poloniex Network Metadata Adapter

Adapts normalized Poloniex network metadata to the
existing ArbOS™ NetworkInfo contract.

Read-only.
No authentication.
No transfers.
No live orders.
"""

from exchanges.network_registry import (
    NetworkInfo,
)


class PoloniexNetworkMetadataAdapter:
    def __init__(
        self,
        provider,
    ):
        if provider is None:
            raise ValueError(
                "provider is required"
            )

        self._provider = provider

    def get_networks(
        self,
        coin,
    ):
        coin = str(
            coin
            or ""
        ).strip().upper()

        if not coin:
            raise ValueError(
                "coin is required"
            )

        result = self._provider.get_coin(
            coin
        )

        if (
            result.get(
                "available"
            )
            is not True
        ):
            return []

        networks = []

        for item in (
            result.get(
                "networks"
            )
            or []
        ):
            network = str(
                item.get(
                    "network",
                    "",
                )
                or ""
            ).strip().upper()

            if not network:
                continue

            fee = item.get(
                "withdraw_fee"
            )

            minimum = item.get(
                "min_withdraw"
            )

            networks.append(
                NetworkInfo(
                    coin=coin,
                    network=network,
                    deposit_enabled=(
                        item.get(
                            "deposit_enabled"
                        )
                        is True
                    ),
                    withdraw_enabled=(
                        item.get(
                            "withdraw_enabled"
                        )
                        is True
                    ),
                    maintenance=False,
                    withdraw_fee=(
                        float(fee)
                        if fee is not None
                        else None
                    ),
                    min_withdraw=float(
                        minimum
                        if minimum is not None
                        else 0.0
                    ),
                )
            )

        return networks

    def describe_networks(
        self,
        coin,
    ):
        coin = str(
            coin
            or ""
        ).strip().upper()

        if not coin:
            raise ValueError(
                "coin is required"
            )

        result = self._provider.get_coin(
            coin
        )

        if (
            result.get(
                "available"
            )
            is not True
        ):
            return {
                "exchange": "poloniex",
                "coin": coin,
                "available": False,
                "network_metadata_available": False,
                "network_metadata_reason": (
                    result.get(
                        "reason",
                        "coin_unavailable",
                    )
                ),
                "transfer_verification_available": False,
                "networks": [],
                "paper_only": True,
                "live_order_submitted": False,
            }

        networks = self.get_networks(
            coin
        )

        metadata_available = result.get(
            "network_metadata_available"
        )

        if metadata_available is None:
            metadata_available = bool(
                networks
            )

        transfer_available = result.get(
            "transfer_verification_available"
        )

        if transfer_available is None:
            transfer_available = bool(
                metadata_available
            )

        return {
            "exchange": "poloniex",
            "coin": coin,
            "available": True,
            "network_metadata_available": (
                bool(metadata_available)
            ),
            "network_metadata_reason": (
                result.get(
                    "network_metadata_reason"
                )
            ),
            "transfer_verification_available": (
                bool(transfer_available)
            ),
            "networks": networks,
            "paper_only": True,
            "live_order_submitted": False,
        }
