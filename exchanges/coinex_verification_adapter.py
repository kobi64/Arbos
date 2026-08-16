"""
ArbOS™
EX-231
CoinEx Verification Adapter

Normalizes CoinEx public order-book depth into the
standard ArbOS™ verification representation.

Read-only.
No authentication.
No orders.
No transfers.
"""


class CoinExVerificationAdapter:
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
    def _normalize_levels(
        levels,
        timestamp=None,
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
            raw = self._client.fetch_order_book(
                symbol,
                limit=limit,
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
        ) != 0:
            return self._failed_result(
                symbol,
                raw.get(
                    "message",
                    "order_book_unavailable",
                ),
            )

        data = raw.get(
            "data"
        )

        if not isinstance(
            data,
            dict,
        ):
            return self._failed_result(
                symbol,
                "invalid_order_book_data",
            )

        depth = data.get(
            "depth"
        )

        if not isinstance(
            depth,
            dict,
        ):
            return self._failed_result(
                symbol,
                "invalid_order_book_depth",
            )

        try:
            timestamp = depth.get(
                "updated_at"
            )

            (
                bids,
                bid_timestamps,
            ) = self._normalize_levels(
                depth.get(
                    "bids",
                    [],
                ),
                timestamp=timestamp,
            )

            (
                asks,
                ask_timestamps,
            ) = self._normalize_levels(
                depth.get(
                    "asks",
                    [],
                ),
                timestamp=timestamp,
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
                "symbol": symbol,
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
            "symbol": symbol,
            "best_bid": None,
            "best_ask": None,
            "bids": [],
            "asks": [],
            "bid_timestamps": [],
            "ask_timestamps": [],
            "reason": reason,
            "paper_only": True,
            "live_order_submitted": False,
        }
