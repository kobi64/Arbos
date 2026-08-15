"""
ArbOS™
EX-221
LBank Verification Provider

Combines the public LBank asset/network metadata client
with LBank network normalization.

Read-only.
No order placement.
No withdrawal submission.
No transfer submission.
"""


class LBankVerificationProvider:
    def __init__(
        self,
        client,
        normalizer,
    ):
        if client is None:
            raise ValueError(
                "client is required"
            )

        if normalizer is None:
            raise ValueError(
                "normalizer is required"
            )

        self._client = client
        self._normalizer = normalizer

    def get_coin(
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

        fetch_result = (
            self._client.fetch_asset_metadata(
                coin
            )
        )

        if (
            fetch_result.get(
                "fetch_complete"
            )
            is not True
        ):
            return {
                "exchange": "lbank",
                "coin": coin,
                "available": False,
                "reason": fetch_result.get(
                    "reason",
                    "asset_metadata_unavailable",
                ),
                "network_metadata_available": False,
                "network_metadata_reason": (
                    "asset_metadata_unavailable"
                ),
                "transfer_verification_available": False,
                "networks": [],
                "paper_only": True,
                "live_order_submitted": False,
                "live_transfer_submitted": False,
            }

        networks = []

        for row in (
            fetch_result.get(
                "networks"
            )
            or []
        ):
            normalized = (
                self._normalizer.normalize_record(
                    row
                )
            )

            if normalized is not None:
                networks.append(
                    normalized
                )

        metadata_available = bool(
            networks
        )

        return {
            "exchange": "lbank",
            "coin": coin,
            "available": True,
            "network_metadata_available": (
                metadata_available
            ),
            "network_metadata_reason": (
                None
                if metadata_available
                else "empty_network_list"
            ),
            "transfer_verification_available": (
                metadata_available
            ),
            "networks": networks,
            "paper_only": True,
            "live_order_submitted": False,
            "live_transfer_submitted": False,
        }
