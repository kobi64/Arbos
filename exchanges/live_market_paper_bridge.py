"""
ArbOS™
EX-068
Live Market Paper Bridge
"""

import math

from exchanges.paper_trading_execution_engine import (
    PaperTradingExecutionEngine,
)


class LiveMarketPaperBridge:
    def __init__(self, market_data_provider):
        self._provider = market_data_provider
        self._paper_engine = PaperTradingExecutionEngine()

    def execute(self, order):
        if order is None:
            raise ValueError("order is required")

        symbol = order.get("symbol")

        if symbol is None or not str(symbol).strip():
            raise ValueError("symbol is required")

        try:
            quantity = float(
                order.get("quantity")
            )
        except (TypeError, ValueError):
            raise ValueError(
                "quantity must be positive"
            )

        if (
            not math.isfinite(quantity)
            or quantity <= 0
        ):
            raise ValueError(
                "quantity must be positive"
            )

        symbol = str(symbol).strip().upper()
        market_price = self._provider.get_price(symbol)

        try:
            market_price = float(
                market_price
            )
        except (TypeError, ValueError):
            raise ValueError(
                "market price unavailable"
            )

        if (
            not math.isfinite(market_price)
            or market_price <= 0
        ):
            raise ValueError(
                "market price unavailable"
            )

        paper_order = dict(order)
        paper_order["symbol"] = symbol
        paper_order["quantity"] = quantity
        paper_order["price"] = market_price

        result = self._paper_engine.execute(paper_order)
        result["market_price"] = market_price
        result["live_order_submitted"] = False

        return result

    def history(self):
        return self._paper_engine.history()
