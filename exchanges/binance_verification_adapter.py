"""
ArbOS™
EX-234
Binance Verification Adapter

Normalizes Binance public SPOT order-book snapshots into the
standard ArbOS™ verification representation.

Verification policy:
- depth snapshot is the primary source
- public bookTicker independently confirms top bid / ask
- mismatches fail closed

Read-only.
No authentication.
No transfers.
No live orders.
"""


class BinanceVerificationAdapter:
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
    def _normalize_symbol(
        symbol,
    ):
        symbol = str(
            symbol
            or ""
        ).strip().upper()

        if not symbol:
            raise ValueError(
                "symbol is required"
            )

        return (
            symbol
            .replace("/", "")
            .replace("-", "")
        )

    @staticmethod
    def _normalize_levels(
        levels,
    ):
        normalized = []

        if not isinstance(
            levels,
            list,
        ):
            raise ValueError(
                "invalid order book levels"
            )

        for level in levels:
            if (
                not isinstance(
                    level,
                    (list, tuple),
                )
                or len(level) < 2
            ):
                raise ValueError(
                    "invalid order book level"
                )

            price = float(
                level[0]
            )

            quantity = float(
                level[1]
            )

            if price <= 0:
                raise ValueError(
                    "price must be positive"
                )

            if quantity < 0:
                raise ValueError(
                    "quantity must not be negative"
                )

            normalized.append([
                price,
                quantity,
            ])

        return normalized

    def fetch_order_book(
        self,
        symbol,
        limit=20,
    ):
        try:
            native_symbol = (
                self._normalize_symbol(
                    symbol
                )
            )

            depth = (
                self._client
                .fetch_order_book(
                    symbol,
                    limit=limit,
                )
            )

            ticker = (
                self._client
                .fetch_book_ticker(
                    symbol
                )
            )

        except Exception as exc:
            return self._failed_result(
                symbol,
                (
                    f"{type(exc).__name__}: "
                    f"{exc}"
                ),
            )

        if not isinstance(
            depth,
            dict,
        ):
            return self._failed_result(
                symbol,
                "invalid_depth_response",
            )

        if not isinstance(
            ticker,
            dict,
        ):
            return self._failed_result(
                symbol,
                "invalid_ticker_response",
            )

        try:
            bids = self._normalize_levels(
                depth.get(
                    "bids",
                    [],
                )
            )

            asks = self._normalize_levels(
                depth.get(
                    "asks",
                    [],
                )
            )

            if not bids or not asks:
                raise ValueError(
                    "empty order book"
                )

            best_bid = bids[0][0]
            best_ask = asks[0][0]

            if best_bid >= best_ask:
                raise ValueError(
                    "crossed or locked order book"
                )

            ticker_symbol = (
                self._normalize_symbol(
                    ticker.get(
                        "symbol"
                    )
                )
            )

            if (
                ticker_symbol
                != native_symbol
            ):
                raise ValueError(
                    "book ticker symbol mismatch"
                )

            ticker_bid = float(
                ticker.get(
                    "bidPrice"
                )
            )

            ticker_ask = float(
                ticker.get(
                    "askPrice"
                )
            )

            if (
                ticker_bid <= 0
                or ticker_ask <= 0
            ):
                raise ValueError(
                    "invalid book ticker"
                )

            if ticker_bid >= ticker_ask:
                raise ValueError(
                    "crossed or locked book ticker"
                )

            if (
                best_bid != ticker_bid
                or best_ask != ticker_ask
            ):
                raise ValueError(
                    "depth / ticker mismatch"
                )

            sequence_id = (
                depth.get(
                    "lastUpdateId"
                )
            )

            return {
                "verification_available": True,
                "verified": True,
                "symbol": str(
                    symbol
                    or ""
                ).strip().upper(),
                "native_symbol": native_symbol,
                "best_bid": best_bid,
                "best_ask": best_ask,
                "bids": bids,
                "asks": asks,
                "bid_timestamps": [],
                "ask_timestamps": [],
                "sequence_id": sequence_id,
                "reason": None,
                "paper_only": True,
                "live_order_submitted": False,
            }

        except Exception as exc:
            return self._failed_result(
                symbol,
                (
                    f"{type(exc).__name__}: "
                    f"{exc}"
                ),
            )

    @staticmethod
    def _failed_result(
        symbol,
        reason,
    ):
        return {
            "verification_available": False,
            "verified": False,
            "symbol": str(
                symbol
                or ""
            ).strip().upper(),
            "native_symbol": None,
            "best_bid": None,
            "best_ask": None,
            "bids": [],
            "asks": [],
            "bid_timestamps": [],
            "ask_timestamps": [],
            "sequence_id": None,
            "reason": reason,
            "paper_only": True,
            "live_order_submitted": False,
        }
