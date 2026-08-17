"""
ArbOS™
EX-226
HTX Network Metadata Adapter

Adapts HTX funding/network metadata into the
standard ArbOS™ network metadata representation.

Current production posture:
- read-only
- credential aware
- fail closed when credentials are unavailable
- no withdrawals
- no transfers
- no live orders
"""

from exchanges.network_registry import (
    NetworkInfo,
)


class HTXNetworkMetadataAdapter:
    def __init__(
        self,
        client,
    ):
        if client is None:
            raise ValueError(
                "client is required"
            )

        self._client = client

    @staticmethod
    def _normalize_coin(
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

        return coin

    @staticmethod
    def _optional_nonnegative_float(
        value,
    ):
        if value in (
            None,
            "",
        ):
            return None

        try:
            value = float(value)
        except (
            TypeError,
            ValueError,
        ):
            return None

        if value < 0:
            return None

        return value

    @staticmethod
    def _normalize_network(
        network,
    ):
        network = str(
            network
            or ""
        ).strip().upper()

        aliases = {
            "ERC20": "ETH",
            "ETHEREUM": "ETH",
            "TRC20": "TRX",
            "TRON": "TRX",
            "BEP20": "BSC",
            "BSC": "BSC",
            "SOLANA": "SOL",
            "SOL": "SOL",
            "ARBITRUM": "ARBITRUM",
            "ARBITRUM ONE": "ARBITRUM",
            "OPTIMISM": "OPTIMISM",
            "BASE": "BASE",
            "BTC": "BTC",
        }

        return aliases.get(
            network,
            network,
        )

    def describe_networks(
        self,
        coin,
    ):
        coin = self._normalize_coin(
            coin
        )

        result = (
            self._client.fetch_currencies()
        )

        if (
            result.get(
                "fetch_complete"
            )
            is not True
        ):
            return {
                "coin": coin,
                "network_metadata_available": False,
                "network_metadata_reason": (
                    result.get(
                        "reason",
                        "network_metadata_unavailable",
                    )
                ),
                "transfer_verification_available": False,
                "networks": [],
                "paper_only": True,
                "live_order_submitted": False,
                "live_transfer_submitted": False,
            }

        currencies = result.get(
            "currencies",
            [],
        )

        if not isinstance(
            currencies,
            list,
        ):
            return {
                "coin": coin,
                "network_metadata_available": False,
                "network_metadata_reason": (
                    "invalid_currency_metadata"
                ),
                "transfer_verification_available": False,
                "networks": [],
                "paper_only": True,
                "live_order_submitted": False,
                "live_transfer_submitted": False,
            }

        networks = []

        for item in currencies:
            if not isinstance(
                item,
                dict,
            ):
                continue

            asset = str(
                item.get(
                    "asset",
                    item.get(
                        "coin",
                        "",
                    ),
                )
                or ""
            ).strip().upper()

            if asset != coin:
                continue

            network = self._normalize_network(
                item.get(
                    "network",
                    item.get(
                        "chain",
                        "",
                    ),
                )
            )

            if not network:
                continue

            withdraw_fee = (
                self._optional_nonnegative_float(
                    item.get(
                        "withdraw_fee",
                        item.get(
                            "withdrawFee"
                        ),
                    )
                )
            )

            min_withdraw = (
                self._optional_nonnegative_float(
                    item.get(
                        "min_withdraw",
                        item.get(
                            "withdrawMin"
                        ),
                    )
                )
            )

            networks.append(
                NetworkInfo(
                    coin=coin,
                    network=network,
                    deposit_enabled=(
                        item.get(
                            "deposit"
                        )
                        is True
                    ),
                    withdraw_enabled=(
                        item.get(
                            "withdraw"
                        )
                        is True
                    ),
                    maintenance=False,
                    withdraw_fee=withdraw_fee,
                    min_withdraw=min_withdraw,
                )
            )

        return {
            "coin": coin,
            "network_metadata_available": True,
            "network_metadata_reason": None,
            "transfer_verification_available": bool(
                networks
            ),
            "networks": networks,
            "paper_only": True,
            "live_order_submitted": False,
            "live_transfer_submitted": False,
        }

    def get_networks(
        self,
        coin,
    ):
        result = self.describe_networks(
            coin
        )

        return result.get(
            "networks",
            [],
        )
