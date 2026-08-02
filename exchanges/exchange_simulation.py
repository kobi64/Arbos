"""
ArbOS™
EX-028
Exchange Simulation Environment

Controlled exchange simulator for testing
execution flows without real funds.
"""

from datetime import datetime, UTC


class ExchangeSimulation:

    VALID_SIDES = {
        "BUY",
        "SELL",
    }

    def __init__(self, exchange_name: str):
        if not exchange_name:
            raise ValueError("exchange_name is required")

        self.exchange_name = exchange_name
        self._history = []

    def simulate_order(
        self,
        symbol: str,
        side: str,
        amount: float,
    ):
        if side not in self.VALID_SIDES:
            raise ValueError("invalid order side")

        if not symbol:
            raise ValueError("symbol is required")

        if amount <= 0:
            raise ValueError("invalid amount")

        record = {
            "timestamp": datetime.now(UTC).isoformat(),
            "exchange": self.exchange_name,
            "status": "filled",
            "symbol": symbol,
            "side": side,
            "amount": amount,
        }

        self._history.append(record)

        return record

    def simulate_partial_fill(
        self,
        order_id: str,
        filled_amount: float,
        requested_amount: float,
    ):
        if not order_id:
            raise ValueError("order_id is required")

        record = {
            "timestamp": datetime.now(UTC).isoformat(),
            "order_id": order_id,
            "status": "partial_fill",
            "filled_amount": filled_amount,
            "requested_amount": requested_amount,
        }

        self._history.append(record)

        return record

    def simulate_failure(
        self,
        order_id: str,
        reason: str,
    ):
        if not order_id:
            raise ValueError("order_id is required")

        record = {
            "timestamp": datetime.now(UTC).isoformat(),
            "order_id": order_id,
            "status": "failed",
            "reason": reason,
        }

        self._history.append(record)

        return record

    def get_history(self):
        return self._history
