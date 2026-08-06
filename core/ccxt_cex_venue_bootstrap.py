"""
ArbOS™
EX-124
CCXT CEX Venue Bootstrap
"""


class CCXTCEXVenueBootstrap:
    def __init__(self, ccxt_module):
        self._ccxt = ccxt_module

    def register_venues(
        self,
        registry,
        exchange_ids,
        enabled=True,
    ):
        for exchange_id in exchange_ids:
            normalized = str(exchange_id).strip().lower()

            if not normalized or not hasattr(self._ccxt, normalized):
                raise ValueError("ccxt exchange not available")

            exchange_class = getattr(self._ccxt, normalized)

            def factory(exchange_class=exchange_class):
                return exchange_class({
                    "enableRateLimit": True,
                })

            registry.register(
                exchange_id=normalized,
                factory=factory,
                enabled=enabled,
            )
