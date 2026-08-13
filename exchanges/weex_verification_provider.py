"""
ArbOS™
EX-217
WEEX Verification Provider

Combines WEEX public market data and network metadata
behind one read-only verification interface.

Responsibilities:
- normalized order books
- normalized coin metadata
- network lookup
- unavailable-result handling

Paper-safe only.
No transfers.
No live orders.
"""


class WeexVerificationProvider:
    def __init__(
        self,
        client,
        adapter,
    ):
        if client is None:
            raise ValueError(
                "client is required"
            )

        if adapter is None:
            raise ValueError(
                "adapter is required"
            )

        self._client = client
        self._adapter = adapter

    def get_order_book(
        self,
        symbol,
        limit=200,
    ):
        symbol = str(
            symbol
            or ""
        ).strip().upper()

        if not symbol:
            raise ValueError(
                "symbol is required"
            )

        depth = self._client.fetch_depth(
            symbol=symbol,
            limit=limit,
        )

        result = self._adapter.normalize_depth(
            depth
        )

        return {
            **result,
            "paper_only": True,
            "live_order_submitted": False,
        }

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
            self._client.fetch_coins()
        )

        if (
            fetch_result.get(
                "fetch_complete"
            )
            is not True
        ):
            return {
                "exchange": "weex",
                "coin": coin,
                "available": False,
                "reason": fetch_result.get(
                    "reason",
                    "coin_metadata_unavailable",
                ),
                "paper_only": True,
                "live_order_submitted": False,
            }

        for coin_data in (
            fetch_result.get(
                "coins"
            )
            or []
        ):
            source_coin = str(
                coin_data.get(
                    "coin",
                    "",
                )
                or ""
            ).strip().upper()

            if source_coin != coin:
                continue

            normalized = (
                self._adapter.normalize_coin(
                    coin_data
                )
            )

            networks = list(
                normalized.get(
                    "networks"
                )
                or []
            )

            network_metadata_available = (
                len(networks) > 0
            )

            return {
                **normalized,
                "available": True,
                "network_metadata_available": (
                    network_metadata_available
                ),
                "network_metadata_reason": (
                    None
                    if network_metadata_available
                    else "empty_network_list"
                ),
                "transfer_verification_available": (
                    network_metadata_available
                ),
                "paper_only": True,
                "live_order_submitted": False,
            }

        return {
            "exchange": "weex",
            "coin": coin,
            "available": False,
            "reason": "coin_not_found",
            "paper_only": True,
            "live_order_submitted": False,
        }

    def get_network(
        self,
        coin,
        network,
    ):
        coin = str(
            coin
            or ""
        ).strip().upper()

        if not coin:
            raise ValueError(
                "coin is required"
            )

        network = str(
            network
            or ""
        ).strip().upper()

        if not network:
            raise ValueError(
                "network is required"
            )

        coin_result = self.get_coin(
            coin
        )

        if (
            coin_result.get(
                "available"
            )
            is not True
        ):
            return {
                "exchange": "weex",
                "coin": coin,
                "network": network,
                "available": False,
                "reason": coin_result.get(
                    "reason",
                    "coin_not_found",
                ),
                "paper_only": True,
                "live_order_submitted": False,
            }

        for network_data in (
            coin_result.get(
                "networks"
            )
            or []
        ):
            source_network = str(
                network_data.get(
                    "network",
                    "",
                )
                or ""
            ).strip().upper()

            if source_network != network:
                continue

            return {
                "exchange": "weex",
                "coin": coin,
                "available": True,
                **dict(
                    network_data
                ),
                "paper_only": True,
                "live_order_submitted": False,
            }

        return {
            "exchange": "weex",
            "coin": coin,
            "network": network,
            "available": False,
            "reason": "network_not_found",
            "paper_only": True,
            "live_order_submitted": False,
        }
