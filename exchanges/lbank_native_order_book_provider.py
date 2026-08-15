"""
ArbOS™
EX-221
LBank Native Order Book Provider

Connects the verified LBank public spot client and
verification adapter to the standard ArbOS™
snapshot(symbol, limit) interface.

Read-only market data.
No authentication.
No transfers.
No live orders.
"""


class LBankNativeOrderBookProvider:
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

    def snapshot(
        self,
        symbol,
        limit=None,
    ):
        symbol = str(
            symbol
            or ""
        ).strip().upper()

        if not symbol:
            raise ValueError(
                "symbol is required"
            )

        if limit is None:
            limit = 20

        raw = self._client.fetch_order_book(
            symbol=symbol,
            limit=limit,
        )

        normalized = (
            self._adapter.normalize_order_book(
                raw
            )
        )

        if (
            normalized.get(
                "available"
            )
            is not True
        ):
            reason = normalized.get(
                "reason",
                "unknown",
            )

            raise RuntimeError(
                "LBank order book unavailable: "
                f"{reason}"
            )

        return {
            "exchange": "lbank",
            "symbol": symbol,
            "timestamp": normalized.get(
                "timestamp"
            ),
            "best_bid": normalized.get(
                "best_bid"
            ),
            "best_ask": normalized.get(
                "best_ask"
            ),
            "bids": self._levels(
                normalized.get(
                    "bids",
                    [],
                )
            ),
            "asks": self._levels(
                normalized.get(
                    "asks",
                    [],
                )
            ),
            "paper_only": True,
            "live_order_submitted": False,
        }

    @staticmethod
    def _levels(
        levels,
    ):
        result = []

        for level in levels:
            if isinstance(
                level,
                dict,
            ):
                result.append([
                    float(
                        level["price"]
                    ),
                    float(
                        level["quantity"]
                    ),
                ])
                continue

            if (
                isinstance(
                    level,
                    (list, tuple),
                )
                and len(level) >= 2
            ):
                result.append([
                    float(level[0]),
                    float(level[1]),
                ])

        return result
