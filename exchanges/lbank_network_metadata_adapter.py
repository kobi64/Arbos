"""
ArbOS™
EX-221
LBank Network Metadata Adapter

Adapts normalized LBank network metadata to the
existing ArbOS™ NetworkInfo contract.

Read-only.
No order placement.
No withdrawal submission.
No transfer submission.
"""

from exchanges.network_registry import (
    NetworkInfo,
)


class LBankNetworkMetadataAdapter:
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
                    min_withdraw=(
                        float(minimum)
                        if minimum is not None
                        else None
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

        networks = self.get_networks(
            coin
        )

        return {
            "exchange": "lbank",
            "coin": coin,
            "available": result.get(
                "available"
            ) is True,
            "network_metadata_available": bool(
                result.get(
                    "network_metadata_available"
                )
            ),
            "network_metadata_reason": result.get(
                "network_metadata_reason"
            ),
            "transfer_verification_available": bool(
                result.get(
                    "transfer_verification_available"
                )
            ),
            "networks": networks,
            "paper_only": True,
            "live_order_submitted": False,
            "live_transfer_submitted": False,
        }
