"""
ArbOS™
EX-233
OKX Verification Adapter

Normalizes OKX public SPOT order-book snapshots into the
standard ArbOS™ verification representation.

OKX returns decimal strings for price and quantity values.

Read-only.
No authentication.
No transfers.
No live orders.
"""


class OKXVerificationAdapter:
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

        if "/" in symbol:
            base, quote = symbol.split(
                "/",
                1,
            )

            base = base.strip()
            quote = quote.strip()

            if not base or not quote:
                raise ValueError(
                    "symbol is required"
                )

            return f"{base}-{quote}"

        return symbol

    @staticmethod
    def _normalize_levels(
        levels,
        timestamp,
    ):
        normalized = []
        timestamps = []

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

            timestamps.append(
                timestamp
            )

        return (
            normalized,
            timestamps,
        )

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

            raw = (
                self._client
                .fetch_order_book(
                    symbol,
                    limit=limit,
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
            raw,
            dict,
        ):
            return self._failed_result(
                symbol,
                "invalid_response",
            )

        if raw.get(
            "code"
        ) != "0":
            return self._failed_result(
                symbol,
                raw.get(
                    "msg",
                    "order_book_unavailable",
                ),
            )

        data = raw.get(
            "data"
        )

        if (
            not isinstance(
                data,
                list,
            )
            or not data
            or not isinstance(
                data[0],
                dict,
            )
        ):
            return self._failed_result(
                symbol,
                "invalid_order_book_data",
            )

        book = data[0]

        try:
            timestamp_raw = book.get(
                "ts"
            )

            timestamp = (
                int(timestamp_raw)
                if timestamp_raw not in (
                    None,
                    "",
                )
                else None
            )

            (
                bids,
                bid_timestamps,
            ) = self._normalize_levels(
                book.get(
                    "bids",
                    [],
                ),
                timestamp,
            )

            (
                asks,
                ask_timestamps,
            ) = self._normalize_levels(
                book.get(
                    "asks",
                    [],
                ),
                timestamp,
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
                "bid_timestamps": (
                    bid_timestamps
                ),
                "ask_timestamps": (
                    ask_timestamps
                ),
                "sequence_id": book.get(
                    "seqId"
                ),
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
