"""
ArbOS™
EX-229
Bitget Network Metadata Adapter

Adapts Bitget public coin/network metadata into the
standard ArbOS™ network metadata representation.

Public read-only metadata.
No authentication.
No withdrawals.
No transfers.
No live orders.
"""


class BitgetNetworkMetadataAdapter:
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
    def _as_bool(
        value,
    ):
        return str(
            value
            or ""
        ).strip().lower() == "true"

    @staticmethod
    def _as_float(
        value,
    ):
        if value in (
            None,
            "",
        ):
            return None

        return float(
            value
        )

    @staticmethod
    def _as_int(
        value,
    ):
        if value in (
            None,
            "",
        ):
            return None

        return int(
            value
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
                    "coin",
                    "",
                )
                or ""
            ).strip().upper()

            if asset != coin:
                continue

            chains = item.get(
                "chains",
                [],
            )

            if not isinstance(
                chains,
                list,
            ):
                continue

            for chain in chains:
                if not isinstance(
                    chain,
                    dict,
                ):
                    continue

                network = str(
                    chain.get(
                        "chain",
                        "",
                    )
                    or ""
                ).strip()

                if not network:
                    continue

                try:
                    normalized = {
                        "network": network,
                        "withdraw_enabled": (
                            self._as_bool(
                                chain.get(
                                    "withdrawable"
                                )
                            )
                        ),
                        "deposit_enabled": (
                            self._as_bool(
                                chain.get(
                                    "rechargeable"
                                )
                            )
                        ),
                        "withdraw_fee": (
                            self._as_float(
                                chain.get(
                                    "withdrawFee"
                                )
                            )
                        ),
                        "deposit_confirmations": (
                            self._as_int(
                                chain.get(
                                    "depositConfirm"
                                )
                            )
                        ),
                        "withdraw_confirmations": (
                            self._as_int(
                                chain.get(
                                    "withdrawConfirm"
                                )
                            )
                        ),
                        "minimum_deposit": (
                            self._as_float(
                                chain.get(
                                    "minDepositAmount"
                                )
                            )
                        ),
                        "minimum_withdrawal": (
                            self._as_float(
                                chain.get(
                                    "minWithdrawAmount"
                                )
                            )
                        ),
                        "contract_address": (
                            chain.get(
                                "contractAddress"
                            )
                        ),
                        "congestion": (
                            chain.get(
                                "congestion"
                            )
                        ),
                        "raw": dict(
                            chain
                        ),
                    }
                except (
                    TypeError,
                    ValueError,
                ):
                    continue

                networks.append(
                    normalized
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
        return self.describe_networks(
            coin
        ).get(
            "networks",
            [],
        )
