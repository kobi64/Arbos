"""
ArbOS™
EX-223
Kraken Network Metadata Adapter

Adapts Kraken funding/network metadata into the
standard ArbOS™ network metadata representation.

Current production posture:
- read-only
- credential aware
- fail closed when credentials are unavailable
- no withdrawals
- no transfers
- no live orders
"""


class KrakenNetworkMetadataAdapter:
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

        return {
            "coin": coin,
            "network_metadata_available": False,
            "network_metadata_reason": (
                "authenticated_metadata_"
                "normalization_not_implemented"
            ),
            "transfer_verification_available": False,
            "networks": [],
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
