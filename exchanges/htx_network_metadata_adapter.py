"""
ArbOS™
EX-226
HTX Network Metadata Adapter

Adapts HTX funding/network metadata into the
standard ArbOS™ network metadata representation.

Current production posture:
- read-only
- credential aware
- fail closed when credentials are unavailable
- no withdrawals
- no transfers
- no live orders
"""


class HTXNetworkMetadataAdapter:
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

            networks.append(
                dict(item)
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
