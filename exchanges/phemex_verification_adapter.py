"""
ArbOS™
EX-232
Phemex Verification Adapter

Normalizes Phemex public spot order-book snapshots into the
standard ArbOS™ verification representation.

Supports:
- explicit fixed scales
- market-specific scale resolution

Read-only.
No authentication.
No orders.
No transfers.
"""


class PhemexVerificationAdapter:
    def __init__(
        self,
        client,
        price_scale=None,
        quantity_scale=None,
        scale_resolver=None,
    ):
        if client is None:
            raise ValueError(
                "client is required"
            )

        if (
            scale_resolver is None
            and (
                price_scale is None
                or quantity_scale is None
            )
        ):
            raise ValueError(
                "scales or scale_resolver are required"
            )

        if price_scale is not None:
            if (
                not isinstance(price_scale, int)
                or isinstance(price_scale, bool)
                or price_scale < 0
            ):
                raise ValueError(
                    "price_scale must be non-negative"
                )

        if quantity_scale is not None:
            if (
                not isinstance(quantity_scale, int)
                or isinstance(quantity_scale, bool)
                or quantity_scale < 0
            ):
                raise ValueError(
                    "quantity_scale must be non-negative"
                )

        self._client = client
        self._price_scale = price_scale
        self._quantity_scale = quantity_scale
        self._scale_resolver = scale_resolver

    @staticmethod
    def _normalize_levels(
        levels,
        price_scale,
        quantity_scale,
        timestamp=None,
    ):
        normalized = []
        timestamps = []

        price_divisor = (
            10 ** price_scale
        )

        quantity_divisor = (
            10 ** quantity_scale
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

            price = (
                float(level[0])
                / price_divisor
            )

            quantity = (
                float(level[1])
                / quantity_divisor
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

    def _resolve_scales(
        self,
        symbol,
    ):
        if self._scale_resolver is not None:
            resolved = (
                self._scale_resolver.resolve(
                    symbol
                )
            )

            if not isinstance(
                resolved,
                dict,
            ):
                raise ValueError(
                    "invalid scale resolution"
                )

            price_scale = resolved.get(
                "price_scale"
            )

            quantity_scale = resolved.get(
                "quantity_scale"
            )

            native_symbol = resolved.get(
                "native_symbol"
            )

        else:
            price_scale = (
                self._price_scale
            )

            quantity_scale = (
                self._quantity_scale
            )

            native_symbol = None

        if (
            not isinstance(price_scale, int)
            or isinstance(price_scale, bool)
            or price_scale < 0
        ):
            raise ValueError(
                "invalid price scale"
            )

        if (
            not isinstance(quantity_scale, int)
            or isinstance(quantity_scale, bool)
            or quantity_scale < 0
        ):
            raise ValueError(
                "invalid quantity scale"
            )

        return {
            "price_scale": price_scale,
            "quantity_scale": quantity_scale,
            "native_symbol": native_symbol,
        }

    def fetch_order_book(
        self,
        symbol,
        limit=30,
    ):
        try:
            scales = self._resolve_scales(
                symbol
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

        if raw.get("error") not in (
            None,
            {},
        ):
            return self._failed_result(
                symbol,
                "order_book_unavailable",
            )

        result = raw.get(
            "result"
        )

        if not isinstance(
            result,
            dict,
        ):
            return self._failed_result(
                symbol,
                "invalid_order_book_result",
            )

        book = result.get(
            "book"
        )

        if not isinstance(
            book,
            dict,
        ):
            return self._failed_result(
                symbol,
                "invalid_order_book",
            )

        try:
            timestamp = result.get(
                "timestamp"
            )

            (
                bids,
                bid_timestamps,
            ) = self._normalize_levels(
                book.get(
                    "bids",
                    [],
                ),
                price_scale=(
                    scales[
                        "price_scale"
                    ]
                ),
                quantity_scale=(
                    scales[
                        "quantity_scale"
                    ]
                ),
                timestamp=timestamp,
            )

            (
                asks,
                ask_timestamps,
            ) = self._normalize_levels(
                book.get(
                    "asks",
                    [],
                ),
                price_scale=(
                    scales[
                        "price_scale"
                    ]
                ),
                quantity_scale=(
                    scales[
                        "quantity_scale"
                    ]
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

            native_symbol = (
                result.get(
                    "symbol"
                )
                or scales.get(
                    "native_symbol"
                )
            )

            return {
                "verification_available": True,
                "verified": True,
                "symbol": symbol,
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
            "native_symbol": None,
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
