"""
ArbOS™
EX-224
Gate.io Network Metadata Adapter

Adapts Gate.io funding/network metadata into the
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


class GateIONetworkMetadataAdapter:
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

        withdrawal_fee_by_network = {}
        default_withdrawal_fee = None

        fetch_currencies = getattr(
            self._client,
            "fetch_currencies",
            None,
        )

        if callable(
            fetch_currencies
        ):
            fee_result = (
                fetch_currencies()
            )

            if (
                isinstance(
                    fee_result,
                    dict,
                )
                and fee_result.get(
                    "fetch_complete"
                )
                is True
            ):
                fee_rows = fee_result.get(
                    "currencies",
                    [],
                )

                if isinstance(
                    fee_rows,
                    list,
                ):
                    for fee_row in fee_rows:
                        if not isinstance(
                            fee_row,
                            dict,
                        ):
                            continue

                        fee_currency = str(
                            fee_row.get(
                                "currency",
                                "",
                            )
                            or ""
                        ).strip().upper()

                        if fee_currency != coin:
                            continue

                        default_withdrawal_fee = (
                            self._optional_nonnegative_float(
                                fee_row.get(
                                    "withdraw_fix"
                                )
                            )
                        )

                        chain_fees = fee_row.get(
                            "withdraw_fix_on_chains",
                            {},
                        )

                        if not isinstance(
                            chain_fees,
                            dict,
                        ):
                            chain_fees = {}

                        for (
                            chain_name,
                            chain_fee,
                        ) in chain_fees.items():
                            chain_name = str(
                                chain_name
                                or ""
                            ).strip().upper()

                            if not chain_name:
                                continue

                            normalized_fee = (
                                self._optional_nonnegative_float(
                                    chain_fee
                                )
                            )

                            if normalized_fee is not None:
                                withdrawal_fee_by_network[
                                    chain_name
                                ] = normalized_fee

                        break

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
                min_withdraw = (
                    self._optional_nonnegative_float(
                        raw.get(
                            "withdraw_amount_min"
                        )
                    )
                )

            withdraw_fee = (
                withdrawal_fee_by_network.get(
                    network
                )
            )

            if withdraw_fee is None:
                withdraw_fee = (
                    default_withdrawal_fee
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
