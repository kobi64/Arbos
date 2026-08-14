"""
ArbOS™
EX-219
MEXC Verification Adapter

Normalizes MEXC public order-book data into the
standard ArbOS™ verification structure.

Public market data only.
No authentication.
No transfers.
No live orders.
"""


class MexcVerificationAdapter:
    def normalize_order_book(
        self,
        result,
    ):
        if result.get(
            "fetch_complete"
        ) is not True:
            return {
                "available": False,
                "symbol": result.get(
                    "symbol"
                ),
                "best_bid": None,
                "best_ask": None,
                "bids": [],
                "asks": [],
                "reason": result.get(
                    "reason",
                    "order_book_unavailable",
                ),
                "paper_only": True,
                "live_order_submitted": False,
            }

        symbol = str(
            result.get(
                "symbol",
                "",
            )
            or ""
        ).strip().upper()

        if not symbol:
            raise ValueError(
                "symbol is required"
            )

        bids = self._normalize_levels(
            result.get(
                "bids",
                [],
            )
        )

        asks = self._normalize_levels(
            result.get(
                "asks",
                [],
            )
        )

        return {
            "available": True,
            "symbol": symbol,
            "best_bid": (
                bids[0]["price"]
                if bids
                else None
            ),
            "best_ask": (
                asks[0]["price"]
                if asks
                else None
            ),
            "bids": bids,
            "asks": asks,
            "reason": None,
            "paper_only": True,
            "live_order_submitted": False,
        }

    @staticmethod
    def _normalize_levels(
        levels,
    ):
        if not isinstance(
            levels,
            list,
        ):
            raise ValueError(
                "order book levels must be a list"
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
                    "order book level must contain price and quantity"
                )

            price = float(
                level[0]
            )

            quantity = float(
                level[1]
            )

            if (
                price <= 0
                or quantity <= 0
            ):
                raise ValueError(
                    "price and quantity must be positive"
                )

            normalized.append({
                "price": price,
                "quantity": quantity,
            })

        return normalized
