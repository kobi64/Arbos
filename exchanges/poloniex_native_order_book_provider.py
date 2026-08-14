"""
ArbOS™
EX-218
Poloniex Native Order Book Provider

Adapts Poloniex public order-book transport and normalization
to the standard ArbOS™ snapshot(symbol, limit) interface.

Public market data only.
No authentication.
No transfers.
No live orders.
"""


class PoloniexNativeOrderBookProvider:
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

        poloniex_symbol = symbol.replace(
            "/",
            "_",
        )

        if limit is None:
            limit = 20

        raw = self._client.fetch_order_book(
            symbol=poloniex_symbol,
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
                "Poloniex order book unavailable: "
                f"{reason}"
            )

        bids = self._levels(
            normalized.get(
                "bids",
                [],
            )
        )

        asks = self._levels(
            normalized.get(
                "asks",
                [],
            )
        )

        return {
            "exchange": "poloniex",
            "symbol": symbol,
            "bids": bids,
            "asks": asks,
            "best_bid": normalized.get(
                "best_bid"
            ),
            "best_ask": normalized.get(
                "best_ask"
            ),
            "paper_only": True,
            "live_order_submitted": False,
        }

    @staticmethod
    def _levels(
        levels,
    ):
        normalized = []

        for level in levels:
            if isinstance(
                level,
                dict,
            ):
                normalized.append([
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
                normalized.append([
                    float(level[0]),
                    float(level[1]),
                ])

        return normalized
