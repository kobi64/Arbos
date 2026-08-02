"""
ArbOS™
EX-049
Exchange Adapter Layer

Provides a standard interface for
multiple exchange connections.
"""


class ExchangeAdapterLayer:

    SUPPORTED_EXCHANGES = {
        "HTX",
        "Gate",
        "KuCoin",
        "Bitget",
        "Uniswap",
    }

    def __init__(self, exchange_name):

        self.exchange_name = exchange_name

    def is_supported(self):

        return self.exchange_name in self.SUPPORTED_EXCHANGES

    def get_balance(self, asset):

        if not self.is_supported():

            return {
                "success": False,
                "reason": "unsupported_exchange",
            }

        return {
            "success": True,
            "asset": asset,
            "balance": 0,
        }

    def create_order(
        self,
        symbol,
        side,
        amount
    ):

        if not self.is_supported():

            return {
                "success": False,
                "reason": "unsupported_exchange",
            }

        return {
            "success": True,
            "exchange": self.exchange_name,
            "symbol": symbol,
            "side": side,
            "amount": amount,
            "order_id": "order-demo",
        }

    def get_order_status(self, order_id):

        return {
            "success": True,
            "order_id": order_id,
            "status": "PENDING",
        }

    def info(self):

        return {
            "exchange": self.exchange_name,
            "supported": self.is_supported(),
        }
