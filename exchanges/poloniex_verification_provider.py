"""
ArbOS™
EX-218
Poloniex Verification Provider

Combines Poloniex public currency metadata with
network normalization for ArbOS™ verification.

Read-only.
No authentication.
No transfers.
No live orders.
"""


class PoloniexVerificationProvider:
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
            self._client.fetch_currencies()
        )

        if (
            fetch_result.get(
                "fetch_complete"
            )
            is not True
        ):
            return {
                "exchange": "poloniex",
                "coin": coin,
                "available": False,
                "reason": fetch_result.get(
                    "reason",
                    "currency_metadata_unavailable",
                ),
                "network_metadata_available": False,
                "network_metadata_reason": (
                    "currency_metadata_unavailable"
                ),
                "transfer_verification_available": False,
                "networks": [],
                "paper_only": True,
                "live_order_submitted": False,
            }

        for row in (
            fetch_result.get(
                "currencies"
            )
            or []
        ):
            source_coin = str(
                row.get(
                    "coin",
                    "",
                )
                or ""
            ).strip().upper()

            if source_coin != coin:
                continue

            raw_networks = (
                row.get(
                    "networkList"
                )
                or []
            )

            networks = [
                self._normalizer.normalize(
                    network
                )
                for network in raw_networks
            ]

            metadata_available = bool(
                networks
            )

            return {
                "exchange": "poloniex",
                "coin": coin,
                "available": True,
                "delisted": bool(
                    row.get(
                        "delisted",
                        False,
                    )
                ),
                "trade_enabled": bool(
                    row.get(
                        "tradeEnable",
                        False,
                    )
                ),
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
            }

        return {
            "exchange": "poloniex",
            "coin": coin,
            "available": False,
            "reason": "coin_not_found",
            "network_metadata_available": False,
            "network_metadata_reason": (
                "coin_not_found"
            ),
            "transfer_verification_available": False,
            "networks": [],
            "paper_only": True,
            "live_order_submitted": False,
        }
