"""
ArbOS™
EX-141
Public CCXT Exchange Bootstrap
"""


class PublicCCXTExchangeBootstrap:
    def __init__(self, ccxt_module):
        self._ccxt = ccxt_module

    def create(self, exchange_id):
        if exchange_id is None or not str(exchange_id).strip():
            raise ValueError("exchange_id is required")

        exchange_id = str(exchange_id).strip().lower()

        exchange_class = getattr(
            self._ccxt,
            exchange_id,
            None,
        )

        if exchange_class is None:
            raise ValueError("unsupported exchange_id")

        config = {
            "enableRateLimit": True,
        }

        return exchange_class(config)
