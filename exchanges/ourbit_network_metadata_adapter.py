"""
ArbOS™
EX-220
Ourbit Network Metadata Adapter

Represents Ourbit currency/network metadata availability.

Current verified state:
- public order books are available
- currency/network metadata endpoint exists
- authenticated signing contract is not yet verified
- therefore transfer verification must fail closed

No order placement.
No withdrawal submission.
No transfer submission.
"""


class OurbitNetworkMetadataAdapter:
    def __init__(
        self,
        client,
    ):
        if client is None:
            raise ValueError(
                "client is required"
            )

        self._client = client

    def get_networks(
        self,
        coin,
    ):
        result = self.fetch(
            coin
        )

        return list(
            result.get(
                "networks",
                [],
            )
            or []
        )

    def describe_networks(
        self,
        coin,
    ):
        return self.fetch(
            coin
        )

    def fetch(
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
            self._client.fetch_currencies()
        )

        if (
            result.get(
                "fetch_complete"
            )
            is not True
        ):
            reason = result.get(
                "reason",
                "network_metadata_unavailable",
            )

            return {
                "exchange": "ourbit",
                "coin": coin,
                "available": False,
                "network_metadata_available": False,
                "network_metadata_reason": reason,
                "transfer_verification_available": False,
                "networks": [],
                "paper_only": True,
                "live_order_submitted": False,
                "live_transfer_submitted": False,
            }

        return {
            "exchange": "ourbit",
            "coin": coin,
            "available": False,
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
