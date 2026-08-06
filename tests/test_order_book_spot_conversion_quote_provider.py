import pytest

from core.order_book_spot_conversion_quote_provider import (
    OrderBookSpotConversionQuoteProvider,
)


class FakeOrderBookProvider:
    def __init__(self):
        self.books = {
            "COINX/BTC": {
                "bids": [
                    [0.00001000, 600.0],
                    [0.00000990, 600.0],
                ],
                "asks": [
                    [0.00001010, 500.0],
                ],
            },
        }

    def get_order_book(self, symbol):
        return self.books.get(symbol)


class FakeDepthEngine:
    def __init__(self):
        self.calls = []

    def evaluate(self, side, quantity, order_book):
        self.calls.append({
            "side": side,
            "quantity": quantity,
            "order_book": order_book,
        })

        return {
            "filled": True,
            "reason": None,
            "requested_quantity": quantity,
            "filled_quantity": quantity,
            "best_price": 0.00001000,
            "average_price": 0.00000995,
            "slippage_percent": 0.5,
            "total_value": 0.00995,
        }


def test_quotes_coin_to_btc_using_sell_side_depth():
    order_books = FakeOrderBookProvider()
    depth = FakeDepthEngine()

    provider = OrderBookSpotConversionQuoteProvider(
        order_book_provider=order_books,
        depth_engine=depth,
    )

    result = provider.quote(
        from_asset="COINX",
        to_asset="BTC",
        amount=1000.0,
    )

    assert result["method"] == "spot"
    assert result["symbol"] == "COINX/BTC"
    assert result["input_amount"] == 1000.0
    assert result["output_amount"] == 0.00995

    assert depth.calls[0]["side"] == "sell"
    assert depth.calls[0]["quantity"] == 1000.0


def test_returns_none_when_order_book_cannot_fill_amount():
    class UnfilledDepthEngine:
        def evaluate(self, side, quantity, order_book):
            return {
                "filled": False,
                "reason": "insufficient_liquidity",
                "requested_quantity": quantity,
                "filled_quantity": 500.0,
                "best_price": 0.00001000,
                "average_price": 0.00001000,
                "slippage_percent": 0.0,
                "total_value": 0.005,
            }

    provider = OrderBookSpotConversionQuoteProvider(
        order_book_provider=FakeOrderBookProvider(),
        depth_engine=UnfilledDepthEngine(),
    )

    result = provider.quote(
        from_asset="COINX",
        to_asset="BTC",
        amount=1000.0,
    )

    assert result is None
