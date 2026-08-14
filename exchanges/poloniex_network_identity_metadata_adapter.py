"""
ArbOS™
EX-218
Poloniex Network Identity Metadata Adapter

Exposes normalized Poloniex network identity evidence
through the existing ArbOS™ get_records(coin) contract.

Contract addresses are preserved when available.
Chain IDs are deliberately not invented.

Read-only.
No authentication.
No transfers.
No live orders.
"""


class PoloniexNetworkIdentityMetadataAdapter:
    def __init__(
        self,
        provider,
    ):
        if provider is None:
            raise ValueError(
                "provider is required"
            )

        self._provider = provider

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

        records = []

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

            contract_address = (
                item.get(
                    "contract_address"
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
                    "deposit_enabled"
                ),
                "withdraw": item.get(
                    "withdraw_enabled"
                ),
                "withdraw_fee": item.get(
                    "withdraw_fee"
                ),
                "raw_info": {
                    "raw_network": item.get(
                        "raw_network"
                    ),
                    "network_name": item.get(
                        "network_name"
                    ),
                    "confirmations": item.get(
                        "confirmations"
                    ),
                },
            })

        return records
