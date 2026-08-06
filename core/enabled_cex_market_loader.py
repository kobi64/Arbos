"""
ArbOS™
EX-125
Enabled CEX Market Loader
"""


class EnabledCEXMarketLoader:
    def __init__(self, registry):
        self._registry = registry

    def load(self):
        markets = {}
        failures = {}

        for exchange_id in self._registry.enabled_exchange_ids():
            try:
                exchange = self._registry.create(exchange_id)
                loaded = exchange.load_markets()

                markets[exchange_id] = loaded

            except Exception as exc:
                failures[exchange_id] = {
                    "reason": "market_load_failed",
                    "error": f"{type(exc).__name__}: {exc}",
                }

        return {
            "markets": markets,
            "failures": failures,
        }
