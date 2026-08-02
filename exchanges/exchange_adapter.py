"""
ArbOS™
EX-027
Exchange Execution Adapter Layer

Provides a controlled interface between
ArbOS execution logic and exchanges.

This foundation uses simulation mode only.
Live execution is intentionally blocked.
"""


from datetime import datetime, UTC


class ExchangeAdapter:

    VALID_SIDES = {
        "BUY",
        "SELL",
    }

    def __init__(self, exchange_name: str):
        if not exchange_name:
            raise ValueError("exchange_name is required")

        self.exchange_name = exchange_name

    def validate_connection(self):
        return {
            "status": "ready",
            "exchange": self.exchange_name,
        }

    def prepare_order(
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

        return {
            "status": "prepared",
            "symbol": symbol,
            "side": side,
            "amount": amount,
        }

    def execute_order(
        self,
        order_id: str,
        simulation: bool = True,
    ):
        if not order_id:
            raise ValueError("order_id is required")

        if not simulation:
            return {
                "status": "blocked",
                "reason": "live execution disabled",
            }

        return {
            "status": "simulated",
            "order_id": order_id,
            "timestamp": datetime.now(UTC).isoformat(),
        }

    def get_status(self):
        return {
            "exchange": self.exchange_name,
            "status": "available",
        }
