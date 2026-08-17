"""
ArbOS™
EX-230
XT Network Metadata Adapter

Adapts XT public network / transfer metadata into the
standard ArbOS™ network metadata representation.

Public read-only metadata.
No authentication.
No withdrawals.
No transfers.
No live orders.
"""


from exchanges.network_registry import (
    NetworkInfo,
)


class XTNetworkMetadataAdapter:
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
    def _normalize_network(
        network,
    ):
        network = str(
            network
            or ""
        ).strip().upper()

        aliases = {
            "BITCOIN": "BTC",
            "BTC": "BTC",
            "BNB SMART CHAIN": "BSC",
            "BSC": "BSC",
            "ETHEREUM": "ETH",
            "ERC20": "ETH",
            "SOLANA": "SOL",
            "SOL": "SOL",
            "TRON": "TRX",
            "TRX": "TRX",
            "ARBITRUM ONE": "ARBITRUM",
            "ARBITRUM": "ARBITRUM",
            "POLYGON POS": "MATIC",
            "MATIC": "MATIC",
            "AVAX C-CHAIN": "AVAXC",
            "AVAXC": "AVAXC",
            "OPTIMISM": "OPTIMISM",
            "BASE": "BASE",
            "APTOS": "APTOS",
            "THE OPEN NETWORK": "TON",
            "TON": "TON",
        }

        return aliases.get(
            network,
            network,
        )

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

        result = self._client.fetch()

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
                    "currency",
                    "",
                )
                or ""
            ).strip().upper()

            if asset != coin:
                continue

            chains = item.get(
                "supportChains",
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
                        "deposit_enabled": bool(
                            chain.get(
                                "depositEnabled"
                            )
                        ),
                        "withdraw_enabled": bool(
                            chain.get(
                                "withdrawEnabled"
                            )
                        ),
                        "deposit_confirmations": (
                            self._as_int(
                                chain.get(
                                    "depositConfirmations"
                                )
                            )
                        ),
                        "minimum_deposit": (
                            self._as_float(
                                chain.get(
                                    "depositMinAmount"
                                )
                            )
                        ),
                        "minimum_withdrawal": (
                            self._as_float(
                                chain.get(
                                    "withdrawMinAmount"
                                )
                            )
                        ),
                        "withdraw_fee": (
                            self._as_float(
                                chain.get(
                                    "withdrawFeeAmount"
                                )
                            )
                        ),
                        "withdraw_fee_currency": str(
                            chain.get(
                                "withdrawFeeCurrency",
                                "",
                            )
                            or ""
                        ).strip().upper(),
                        "contract_address": (
                            chain.get(
                                "contract"
                            )
                        ),
                        "withdraw_precision": (
                            self._as_int(
                                chain.get(
                                    "withdrawPrecision"
                                )
                            )
                        ),
                        "deposit_fee_rate": (
                            self._as_float(
                                chain.get(
                                    "depositFeeRate"
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
                    NetworkInfo(
                        coin=coin,
                        network=(
                            self._normalize_network(
                                normalized[
                                    "network"
                                ]
                            )
                        ),
                        deposit_enabled=(
                            normalized[
                                "deposit_enabled"
                            ]
                        ),
                        withdraw_enabled=(
                            normalized[
                                "withdraw_enabled"
                            ]
                        ),
                        maintenance=False,
                        withdraw_fee=(
                            normalized[
                                "withdraw_fee"
                            ]
                        ),
                        min_withdraw=(
                            normalized[
                                "minimum_withdrawal"
                            ]
                        ),
                        confirmations=(
                            normalized[
                                "deposit_confirmations"
                            ]
                            or 0
                        ),
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
        return self.describe_networks(
            coin
        ).get(
            "networks",
            [],
        )
