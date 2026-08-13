"""
ArbOS™
EX-217
WEEX Native Order Book Provider

Adapts the WEEX verification provider to the standard
ArbOS™ snapshot(symbol, limit) order-book interface.

Public market data / paper valuation only.
No authentication.
No transfers.
No live orders.
"""


class WeexNativeOrderBookProvider:
    def __init__(
        self,
        provider,
    ):
        if provider is None:
            raise ValueError(
                "provider is required"
            )

        self._provider = provider

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

        weex_symbol = (
            symbol.replace(
                "/",
                "",
            )
        )

        if limit is None:
            limit = 200

        result = (
            self._provider.get_order_book(
                symbol=weex_symbol,
                limit=limit,
            )
        )

        if (
            result.get(
                "available"
            )
            is not True
        ):
            reason = result.get(
                "reason",
                "unknown",
            )

            raise RuntimeError(
                "WEEX order book unavailable: "
                f"{reason}"
            )

        bids = self._levels(
            result.get(
                "bids",
                [],
            )
        )

        asks = self._levels(
            result.get(
                "asks",
                [],
            )
        )

        return {
            "exchange": "weex",
            "symbol": symbol,
            "bids": bids,
            "asks": asks,
            "best_bid": result.get(
                "best_bid"
            ),
            "best_ask": result.get(
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
