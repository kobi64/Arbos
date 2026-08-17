"""
ArbOS™
EX-260
KuCoin Network Identity Metadata Adapter

Exposes public KuCoin network identity evidence through the
existing ArbOS™ get_records(coin) contract.

Contract addresses are preserved when available.
KuCoin exchange chain labels are not promoted to authoritative
blockchain chain IDs.

Read-only.
No order placement.
No withdrawal submission.
No transfer submission.
"""


class KuCoinNetworkIdentityMetadataAdapter:
    def __init__(
        self,
        client,
    ):
        if client is None:
            raise ValueError(
                "client is required"
            )

        self._client = client

    def get_records(
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

        result = (
            self._client.fetch_currency_chains(
                coin
            )
        )

        if (
            result.get(
                "fetch_complete"
            )
            is not True
        ):
            return []

        currencies = result.get(
            "currencies",
            [],
        )

        if not isinstance(
            currencies,
            list,
        ):
            return []

        records = []

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

            contract_address = (
                item.get(
                    "contract_address"
                )
                or item.get(
                    "contractAddress"
                )
                or raw.get(
                    "contract_address"
                )
                or raw.get(
                    "contractAddress"
                )
            )

            if contract_address is not None:
                contract_address = str(
                    contract_address
                ).strip() or None

            records.append({
                "coin": coin,
                "network": network,
                "network_name": network,
                "chain_id": None,
                "contract_address": (
                    contract_address
                ),
                "deposit": item.get(
                    "deposit"
                ),
                "withdraw": item.get(
                    "withdraw"
                ),
                "raw_info": raw,
            })

        return records
