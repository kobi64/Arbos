"""
ArbOS™
EX-181
DigiFinex Native Order Book Source

Provides normalized public spot order-book snapshots for
DigiFinex RAW_ONLY markets that CCXT does not expose through
its normalized market catalogue.

Public market data only.
No authentication.
No transfers.
No live orders.
"""


class DigiFinexNativeOrderBookSource:
    def __init__(self, exchange):
        if exchange is None:
            raise ValueError("exchange is required")

        self._exchange = exchange

    def snapshot(self, symbol, limit=None):
        if symbol is None or not str(symbol).strip():
            raise ValueError("symbol is required")

        symbol = str(symbol).strip().upper()

        parts = [
            part.strip()
            for part in symbol.split("/")
            if part.strip()
        ]

        if len(parts) != 2:
            raise ValueError("symbol must be BASE/QUOTE")

        raw_symbol = (
            f"{parts[0].lower()}_"
            f"{parts[1].lower()}"
        )

        method = getattr(
            self._exchange,
            "publicSpotGetOrderBook",
            None,
        )

        if not callable(method):
            method = getattr(
                self._exchange,
                "public_spot_get_order_book",
                None,
            )

        if not callable(method):
            raise ValueError(
                "digifinex native order book unavailable"
            )

        params = {
            "symbol": raw_symbol,
        }

        if limit is not None:
            params["limit"] = int(limit)

        response = method(params)

        if not isinstance(response, dict):
            raise ValueError(
                "invalid native order book response"
            )

        if response.get("code") not in {
            None,
            0,
            "0",
        }:
            raise ValueError(
                "native order book request failed"
            )

        raw_bids = response.get("bids") or []
        raw_asks = response.get("asks") or []

        if not raw_bids or not raw_asks:
            raise ValueError(
                "order book unavailable"
            )

        bids = sorted(
            [
                [float(level[0]), float(level[1])]
                for level in raw_bids
                if isinstance(level, (list, tuple))
                and len(level) >= 2
            ],
            key=lambda level: level[0],
            reverse=True,
        )

        asks = sorted(
            [
                [float(level[0]), float(level[1])]
                for level in raw_asks
                if isinstance(level, (list, tuple))
                and len(level) >= 2
            ],
            key=lambda level: level[0],
        )

        if not bids or not asks:
            raise ValueError(
                "order book unavailable"
            )

        return {
            "symbol": symbol,
            "bids": bids,
            "asks": asks,
            "best_bid": float(
                bids[0][0]
            ),
            "best_ask": float(
                asks[0][0]
            ),
            "timestamp": response.get(
                "date"
            ),
            "datetime": None,
            "market_source": (
                "DIGIFINEX_NATIVE"
            ),
            "paper_only": True,
            "live_order_submitted": False,
        }
