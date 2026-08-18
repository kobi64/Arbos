"""
ArbOS™
EX-235
Coinbase Network Metadata Adapter

Normalizes Coinbase Exchange public currency/network metadata
into the standard ArbOS™ network representation.

Read-only.
No authentication.
No transfer submission.
No withdrawal submission.
"""


class CoinbaseNetworkMetadataAdapter:
    def __init__(
        self,
        client,
    ):
        if client is None:
            raise ValueError(
                "client is required"
            )

        self._client = client

    def list_networks(
        self,
        currency=None,
    ):
        try:
            payload = (
                self._client
                .fetch_currencies()
            )
        except Exception as exc:
            raise RuntimeError(
                "Coinbase currencies unavailable: "
                f"{type(exc).__name__}: "
                f"{exc}"
            ) from exc

        if not isinstance(
            payload,
            list,
        ):
            raise RuntimeError(
                "Coinbase currencies unavailable: "
                "invalid response"
            )

        currency_filter = (
            str(
                currency
                or ""
            ).strip().upper()
            or None
        )

        results = []

        for item in payload:
            if not isinstance(
                item,
                dict,
            ):
                continue

            currency_id = str(
                item.get(
                    "id",
                    "",
                )
                or ""
            ).strip().upper()

            if not currency_id:
                continue

            if (
                currency_filter is not None
                and currency_id
                != currency_filter
            ):
                continue

            if (
                str(
                    item.get(
                        "status",
                        "",
                    )
                ).strip().lower()
                != "online"
            ):
                continue

            default_network = str(
                item.get(
                    "default_network",
                    "",
                )
                or ""
            ).strip().lower()

            networks = item.get(
                "supported_networks",
                [],
            )

            if not isinstance(
                networks,
                list,
            ):
                continue

            for network in networks:
                if not isinstance(
                    network,
                    dict,
                ):
                    continue

                if (
                    str(
                        network.get(
                            "status",
                            "",
                        )
                    ).strip().lower()
                    != "online"
                ):
                    continue

                network_id = str(
                    network.get(
                        "id",
                        "",
                    )
                    or ""
                ).strip().lower()

                network_name = str(
                    network.get(
                        "name",
                        "",
                    )
                    or ""
                ).strip()

                if not network_id:
                    continue

                results.append({
                    "currency": currency_id,
                    "network": network_id,
                    "network_name": (
                        network_name
                        or network_id
                    ),
                    "active": True,
                    "deposit_enabled": None,
                    "withdraw_enabled": None,
                    "withdraw_fee": None,
                    "transfer_verification_available": False,
                    "default": (
                        network_id
                        == default_network
                    ),
                    "contract_address": (
                        network.get(
                            "contract_address"
                        )
                    ),
                    "min_withdrawal": (
                        network.get(
                            "min_withdrawal_amount"
                        )
                    ),
                    "max_withdrawal": (
                        network.get(
                            "max_withdrawal_amount"
                        )
                    ),
                    "confirmations": (
                        network.get(
                            "network_confirmations"
                        )
                    ),
                    "processing_time_seconds": (
                        network.get(
                            "processing_time_seconds"
                        )
                    ),
                    "destination_tag_regex": (
                        network.get(
                            "destination_tag_regex"
                        )
                    ),
                    "is_evm": (
                        network.get(
                            "is_evm_network"
                        )
                    ),
                })

        return results
