"""
ArbOS™
EX-067
Paper Trading Execution Engine
"""

from datetime import UTC, datetime


class PaperTradingExecutionEngine:
    def __init__(self):
        self._history = []
        self._sequence = 0

    def execute(self, order):
        if order is None:
            raise ValueError("order is required")

        symbol = order.get("symbol")
        quantity = order.get("quantity")
        price = order.get("price")

        if symbol is None or not str(symbol).strip():
            raise ValueError("symbol is required")

        try:
            quantity = float(quantity)
        except (TypeError, ValueError):
            quantity = 0.0

        if quantity <= 0:
            raise ValueError("quantity must be positive")

        try:
            price = float(price)
        except (TypeError, ValueError):
            raise ValueError("price is required")

        if price <= 0:
            raise ValueError("price must be positive")

        self._sequence += 1
        paper_order_id = f"PAPER-{self._sequence:06d}"

        record = {
            "paper_order_id": paper_order_id,
            "symbol": str(symbol).strip().upper(),
            "status": "FILLED",
            "paper_trade": True,
            "filled_quantity": quantity,
            "average_price": price,
            "notional": quantity * price,
            "executed_at": datetime.now(UTC).isoformat(),
        }

        self._history.append(record)
        return dict(record)

    def history(self):
        return [dict(record) for record in self._history]
