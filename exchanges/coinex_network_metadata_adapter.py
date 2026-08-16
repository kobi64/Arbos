"""
ArbOS™
EX-231
CoinEx Network Metadata Adapter

Adapts CoinEx public deposit / withdrawal configuration
into the standard ArbOS™ network metadata representation.

Read-only.
No authentication.
No transfers.
No live orders.
"""


class CoinExNetworkMetadataAdapter:
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

        try:
            result = (
                self._client
                .fetch_currency_metadata(
                    coin
                )
            )
        except Exception as exc:
            return {
                "coin": coin,
                "network_metadata_available": False,
                "network_metadata_reason": (
                    f"{type(exc).__name__}: "
                    f"{exc}"
                ),
                "transfer_verification_available": False,
                "networks": [],
                "paper_only": True,
                "live_order_submitted": False,
                "live_transfer_submitted": False,
            }

        if not isinstance(
            result,
            dict,
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

        chains = result.get(
            "chains",
            [],
        )

        if not isinstance(
            chains,
            list,
        ):
            return {
                "coin": coin,
                "network_metadata_available": False,
                "network_metadata_reason": (
                    "invalid_chain_metadata"
                ),
                "transfer_verification_available": False,
                "networks": [],
                "paper_only": True,
                "live_order_submitted": False,
                "live_transfer_submitted": False,
            }

        networks = []

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
                    "deposit_enabled": (
                        chain.get(
                            "deposit_enabled"
                        )
                        is True
                    ),
                    "withdraw_enabled": (
                        chain.get(
                            "withdraw_enabled"
                        )
                        is True
                    ),
                    "minimum_deposit": (
                        self._as_float(
                            chain.get(
                                "min_deposit_amount"
                            )
                        )
                    ),
                    "minimum_withdrawal": (
                        self._as_float(
                            chain.get(
                                "min_withdraw_amount"
                            )
                        )
                    ),
                    "withdraw_fee": (
                        self._as_float(
                            chain.get(
                                "withdrawal_fee"
                            )
                        )
                    ),
                    "safe_confirmations": (
                        self._as_int(
                            chain.get(
                                "safe_confirmations"
                            )
                        )
                    ),
                    "irreversible_confirmations": (
                        self._as_int(
                            chain.get(
                                "irreversible_confirmations"
                            )
                        )
                    ),
                    "withdraw_precision": (
                        self._as_int(
                            chain.get(
                                "withdrawal_precision"
                            )
                        )
                    ),
                    "deposit_delay_minutes": (
                        self._as_int(
                            chain.get(
                                "deposit_delay_minutes"
                            )
                        )
                    ),
                    "memo_required": (
                        chain.get(
                            "is_memo_required_for_deposit"
                        )
                        is True
                    ),
                    "memo_label": str(
                        chain.get(
                            "memo",
                            "",
                        )
                        or ""
                    ),
                    "explorer_asset_url": (
                        chain.get(
                            "explorer_asset_url"
                        )
                    ),
                    "deflation_rate": (
                        self._as_float(
                            chain.get(
                                "deflation_rate"
                            )
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
