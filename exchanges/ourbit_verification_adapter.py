"""
ArbOS™
EX-220
Ourbit Verification Adapter

Normalizes Ourbit public depth data into the
standard ArbOS™ order-book verification structure.

Read-only.
No transfers.
No live orders.
"""


class OurbitVerificationAdapter:
    def normalize_order_book(
        self,
        payload,
    ):
        payload = (
            payload
            if isinstance(payload, dict)
            else {}
        )

        if (
            payload.get("fetch_complete")
            is not True
        ):
            return self._unavailable(
                payload.get(
                    "reason",
                    "request_failed",
                )
            )

        bids = payload.get(
            "bids",
            [],
        )

        asks = payload.get(
            "asks",
            [],
        )

        if not bids or not asks:
            return self._unavailable(
                "empty_order_book"
            )

        try:
            normalized_bids = (
                self._normalize_levels(
                    bids
                )
            )

            normalized_asks = (
                self._normalize_levels(
                    asks
                )
            )

        except (
            TypeError,
            ValueError,
            IndexError,
            KeyError,
        ):
            return self._unavailable(
                "invalid_order_book"
            )

        if (
            not normalized_bids
            or not normalized_asks
        ):
            return self._unavailable(
                "empty_order_book"
            )

        return {
            "available": True,
            "reason": None,
            "symbol": payload.get(
                "symbol"
            ),
            "timestamp": payload.get(
                "timestamp"
            ),
            "best_bid": (
                normalized_bids[0][
                    "price"
                ]
            ),
            "best_ask": (
                normalized_asks[0][
                    "price"
                ]
            ),
            "bids": normalized_bids,
            "asks": normalized_asks,
            "paper_only": True,
            "live_order_submitted": False,
        }

    @staticmethod
    def _normalize_levels(
        levels,
    ):
        result = []

        for level in levels:
            if (
                not isinstance(
                    level,
                    (list, tuple),
                )
                or len(level) < 2
            ):
                raise ValueError(
                    "invalid order-book level"
                )

            price = float(
                level[0]
            )

            quantity = float(
                level[1]
            )

            if (
                price <= 0
                or quantity < 0
            ):
                raise ValueError(
                    "invalid order-book values"
                )

            result.append({
                "price": price,
                "quantity": quantity,
            })

        return result

    @staticmethod
    def _unavailable(
        reason,
    ):
        return {
            "available": False,
            "reason": reason,
            "symbol": None,
            "timestamp": None,
            "best_bid": None,
            "best_ask": None,
            "bids": [],
            "asks": [],
            "paper_only": True,
            "live_order_submitted": False,
        }
