"""
ArbOS™
EX-131
Order-Book Spot Conversion Quote Provider
"""


class OrderBookSpotConversionQuoteProvider:
    def __init__(
        self,
        order_book_provider,
        depth_engine,
    ):
        self._order_book_provider = order_book_provider
        self._depth_engine = depth_engine

    def quote(
        self,
        from_asset,
        to_asset,
        amount,
    ):
        if amount <= 0:
            raise ValueError("amount must be positive")

        from_asset = str(from_asset).strip().upper()
        to_asset = str(to_asset).strip().upper()

        if not from_asset:
            raise ValueError("from_asset is required")

        if not to_asset:
            raise ValueError("to_asset is required")

        symbol = f"{from_asset}/{to_asset}"

        order_book = self._order_book_provider.get_order_book(
            symbol
        )

        if not order_book:
            return None

        depth = self._depth_engine.evaluate(
            side="sell",
            quantity=float(amount),
            order_book=order_book,
        )

        if not depth.get("filled"):
            return None

        return {
            "available": True,
            "method": "spot",
            "symbol": symbol,
            "from_asset": from_asset,
            "to_asset": to_asset,
            "input_amount": float(amount),
            "output_amount": depth["total_value"],
            "filled_quantity": depth["filled_quantity"],
            "best_price": depth["best_price"],
            "average_price": depth["average_price"],
            "slippage_percent": depth["slippage_percent"],
        }
