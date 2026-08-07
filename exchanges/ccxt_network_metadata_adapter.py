"""
ArbOS™
EX-139
CCXT Network Metadata Adapter
"""

from exchanges.network_registry import (
    NetworkInfo,
)


class CCXTNetworkMetadataAdapter:
    def __init__(self, exchange):
        self._exchange = exchange
        self._currencies = self._exchange.load_currencies()

    def get_networks(self, coin):
        if coin is None or not str(coin).strip():
            raise ValueError("coin is required")

        coin = str(coin).strip().upper()

        currency = self._currencies.get(coin)

        if not currency:
            return []

        currency_deposit = currency.get(
            "deposit",
            True,
        )

        currency_withdraw = currency.get(
            "withdraw",
            True,
        )

        networks = currency.get("networks") or {}

        results = []

        for network_name, network in networks.items():
            limits = network.get("limits") or {}
            withdraw_limits = (
                limits.get("withdraw") or {}
            )

            min_withdraw = withdraw_limits.get(
                "min"
            )

            fee = network.get("fee")

            deposit_enabled = network.get(
                "deposit",
                currency_deposit,
            )

            withdraw_enabled = network.get(
                "withdraw",
                currency_withdraw,
            )

            results.append(
                NetworkInfo(
                    coin=coin,
                    network=str(
                        network_name
                    ).strip().upper(),
                    deposit_enabled=(
                        deposit_enabled is not False
                    ),
                    withdraw_enabled=(
                        withdraw_enabled is not False
                    ),
                    maintenance=False,
                    withdraw_fee=float(
                        fee
                        if fee is not None
                        else 0.0
                    ),
                    min_withdraw=float(
                        min_withdraw
                        if min_withdraw is not None
                        else 0.0
                    ),
                )
            )

        return results
