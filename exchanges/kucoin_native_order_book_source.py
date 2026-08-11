"""
ArbOS™
EX-184
KuCoin Native Order Book Source

Retrieves and normalizes KuCoin native public spot order-book depth.

Public market data only.
No authentication.
No transfers.
No live orders.
"""


class KuCoinNativeOrderBookSource:
    def __init__(self, exchange):
        if exchange is None:
            raise ValueError("exchange is required")

        self._exchange = exchange

    def snapshot(
        self,
        symbol,
        limit=None,
    ):
        if symbol is None or not str(symbol).strip():
            raise ValueError("symbol is required")

        symbol = str(
            symbol
        ).strip().upper()

        native_symbol = symbol.replace(
            "/",
            "-",
        )

        response = (
            self._exchange
            .publicGetMarketOrderbookLevel220({
                "symbol": native_symbol,
            })
        )

        if not isinstance(response, dict):
            raise ValueError(
                "invalid KuCoin order book response"
            )

        data = response.get("data")

        if not isinstance(data, dict):
            raise ValueError(
                "invalid KuCoin order book data"
            )

        bids = self._normalize_levels(
            data.get("bids", [])
        )

        asks = self._normalize_levels(
            data.get("asks", [])
        )

        return {
            "symbol": symbol,
            "bids": bids,
            "asks": asks,
            "timestamp": data.get("time"),
            "sequence": data.get("sequence"),
            "market_source": "KUCOIN_NATIVE",
        }

    @staticmethod
    def _normalize_levels(levels):
        normalized = []

        for level in levels:
            if (
                not isinstance(level, (list, tuple))
                or len(level) < 2
            ):
                continue

            normalized.append([
                float(level[0]),
                float(level[1]),
            ])

        return normalized
