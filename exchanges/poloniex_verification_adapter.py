"""
ArbOS™
EX-218
Poloniex Verification Adapter

Normalizes Poloniex public order-book data into the
standard ArbOS™ verification structure.

Public market data only.
No authentication.
No transfers.
No live orders.
"""


class PoloniexVerificationAdapter:
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

        bids = self._normalize_flat_depth(
            result.get(
                "bids",
                [],
            )
        )

        asks = self._normalize_flat_depth(
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
    def _normalize_flat_depth(
        values,
    ):
        if not isinstance(
            values,
            list,
        ):
            raise ValueError(
                "depth must be a list"
            )

        if len(values) % 2 != 0:
            raise ValueError(
                "depth must contain price/quantity pairs"
            )

        normalized = []

        for index in range(
            0,
            len(values),
            2,
        ):
            price = float(
                values[index]
            )

            quantity = float(
                values[index + 1]
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
