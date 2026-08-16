"""
ArbOS™
EX-235
Coinbase Verification Adapter

Normalizes Coinbase Exchange public Level-2 order-book snapshots
into the standard ArbOS™ verification representation.

Verification policy:
- Level-2 order book is the primary source
- public ticker independently confirms top bid / ask
- mismatches fail closed

Read-only.
No authentication.
No transfers.
No live orders.
"""


class CoinbaseVerificationAdapter:
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
    def _normalize_product_id(
        product_id,
    ):
        product_id = str(
            product_id
            or ""
        ).strip().upper()

        if not product_id:
            raise ValueError(
                "product_id is required"
            )

        return (
            product_id
            .replace("/", "-")
            .replace("_", "-")
        )

    @staticmethod
    def _normalize_levels(
        levels,
    ):
        if not isinstance(
            levels,
            list,
        ):
            raise ValueError(
                "invalid order book levels"
            )

        normalized = []

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
        product_id,
        level=2,
    ):
        try:
            native_symbol = (
                self._normalize_product_id(
                    product_id
                )
            )

            book = (
                self._client
                .fetch_order_book(
                    product_id,
                    level=level,
                )
            )

            ticker = (
                self._client
                .fetch_ticker(
                    product_id
                )
            )

        except Exception as exc:
            return self._failed_result(
                product_id,
                (
                    f"{type(exc).__name__}: "
                    f"{exc}"
                ),
            )

        if not isinstance(
            book,
            dict,
        ):
            return self._failed_result(
                product_id,
                "invalid_order_book_response",
            )

        if not isinstance(
            ticker,
            dict,
        ):
            return self._failed_result(
                product_id,
                "invalid_ticker_response",
            )

        try:
            bids = self._normalize_levels(
                book.get(
                    "bids",
                    [],
                )
            )

            asks = self._normalize_levels(
                book.get(
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

            ticker_bid = float(
                ticker.get(
                    "bid"
                )
            )

            ticker_ask = float(
                ticker.get(
                    "ask"
                )
            )

            if (
                ticker_bid <= 0
                or ticker_ask <= 0
            ):
                raise ValueError(
                    "invalid ticker"
                )

            if ticker_bid >= ticker_ask:
                raise ValueError(
                    "crossed or locked ticker"
                )

            if (
                best_bid != ticker_bid
                or best_ask != ticker_ask
            ):
                raise ValueError(
                    "order book / ticker mismatch"
                )

            return {
                "verification_available": True,
                "verified": True,
                "symbol": str(
                    product_id
                    or ""
                ).strip().upper(),
                "native_symbol": native_symbol,
                "best_bid": best_bid,
                "best_ask": best_ask,
                "bids": bids,
                "asks": asks,
                "bid_timestamps": [],
                "ask_timestamps": [],
                "sequence_id": book.get(
                    "sequence"
                ),
                "reason": None,
                "paper_only": True,
                "live_order_submitted": False,
            }

        except Exception as exc:
            return self._failed_result(
                product_id,
                (
                    f"{type(exc).__name__}: "
                    f"{exc}"
                ),
            )

    @staticmethod
    def _failed_result(
        product_id,
        reason,
    ):
        return {
            "verification_available": False,
            "verified": False,
            "symbol": str(
                product_id
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
