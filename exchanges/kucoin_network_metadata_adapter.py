"""
ArbOS™
EX-225
KuCoin Network Metadata Adapter

Adapts KuCoin funding/network metadata into the
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


class KuCoinNetworkMetadataAdapter:
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

    def describe_networks(
        self,
        coin,
    ):
        coin = self._normalize_coin(
            coin
        )

        fetch_currency_chains = getattr(
            self._client,
            "fetch_currency_chains",
            None,
        )

        if callable(
            fetch_currency_chains
        ):
            result = (
                fetch_currency_chains(
                    coin
                )
            )
        else:
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

            network = str(
                item.get(
                    "network",
                    item.get(
                        "chain",
                        "",
                    ),
                )
                or ""
            ).strip().upper()

            if not network:
                continue

            raw = item.get(
                "raw",
                {},
            )

            if not isinstance(
                raw,
                dict,
            ):
                raw = {}

            min_withdraw = (
                self._optional_nonnegative_float(
                    item.get(
                        "min_withdraw"
                    )
                )
            )

            if min_withdraw is None:
                for key in (
                    "withdrawMinSize",
                    "withdrawalMinSize",
                ):
                    min_withdraw = (
                        self._optional_nonnegative_float(
                            raw.get(key)
                        )
                    )

                    if min_withdraw is not None:
                        break

            withdraw_fee = (
                self._optional_nonnegative_float(
                    item.get(
                        "withdraw_fee"
                    )
                )
            )

            if withdraw_fee is None:
                for key in (
                    "withdrawMinFee",
                    "withdrawalMinFee",
                ):
                    withdraw_fee = (
                        self._optional_nonnegative_float(
                            raw.get(key)
                        )
                    )

                    if withdraw_fee is not None:
                        break

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
