"""
ArbOS™
EX-178
CCXT Network Identity Metadata Adapter

Extracts stronger blockchain identity evidence from exchange
currency/network metadata for EX-177 verification.

This adapter is deliberately separate from the legacy network
metadata adapter used for fees and transfer feasibility.

No transfers or live orders are submitted.
"""


class CCXTNetworkIdentityMetadataAdapter:
    def __init__(self, exchange):
        if exchange is None:
            raise ValueError("exchange is required")

        self._exchange = exchange
        self._currencies = self._load_currencies()

    def _load_currencies(self):
        fetch_currencies = getattr(
            self._exchange,
            "fetch_currencies",
            None,
        )

        if callable(fetch_currencies):
            try:
                currencies = fetch_currencies()
                if currencies:
                    return currencies
            except Exception:
                pass

        load_currencies = getattr(
            self._exchange,
            "load_currencies",
            None,
        )

        if callable(load_currencies):
            try:
                currencies = load_currencies()
                if currencies:
                    return currencies
            except Exception:
                pass

        self._exchange.load_markets()

        return (
            getattr(
                self._exchange,
                "currencies",
                {},
            )
            or {}
        )

    def get_records(self, coin):
        if coin is None or not str(coin).strip():
            raise ValueError("coin is required")

        coin = str(coin).strip().upper()

        currency = self._currencies.get(coin)

        if not currency:
            return []

        currency_deposit = currency.get(
            "deposit",
            None,
        )

        currency_withdraw = currency.get(
            "withdraw",
            None,
        )

        records = []

        for network_name, network in (
            currency.get("networks") or {}
        ).items():
            info = network.get("info") or {}

            chain_id = (
                info.get("chainId")
                or info.get("chain_id")
                or info.get("chain")
                or None
            )

            if chain_id is not None:
                chain_id = str(
                    chain_id
                ).strip() or None

            contract_address = (
                info.get("contractAddress")
                or info.get("contract_address")
                or network.get(
                    "contractAddress"
                )
                or network.get(
                    "contract_address"
                )
                or None
            )

            if contract_address is not None:
                contract_address = str(
                    contract_address
                ).strip() or None

            records.append({
                "coin": coin,
                "network": str(
                    network_name
                ).strip().upper(),
                "network_name": str(
                    network_name
                ).strip().upper(),
                "chain_id": chain_id,
                "contract_address": (
                    contract_address
                ),
                "deposit": network.get(
                    "deposit",
                    currency_deposit,
                ),
                "withdraw": network.get(
                    "withdraw",
                    currency_withdraw,
                ),
                "withdraw_fee": network.get(
                    "fee"
                ),
                "raw_info": info,
            })

        return records
