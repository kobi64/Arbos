"""
ArbOS™
EX-182 / EX-183
Verified Native Order Book Provider Factory

Selects the appropriate public order-book provider for an exchange.

Native fallback providers are supplied through the
NativeFallbackExchangeRegistry.

Unregistered exchanges continue using the normal CCXT snapshot engine.

Public market data / paper valuation only.
No authentication.
No transfers.
No live orders.
"""

from exchanges.live_order_book_snapshot_engine import (
    LiveOrderBookSnapshotEngine,
)
from exchanges.native_fallback_exchange_registry import (
    NativeFallbackExchangeRegistry,
)
from exchanges.verified_digifinex_order_book_provider import (
    VerifiedDigiFinexOrderBookProvider,
)


class VerifiedNativeOrderBookProviderFactory:
    def __init__(self, registry=None):
        if registry is None:
            registry = NativeFallbackExchangeRegistry()

            registry.register(
                "digifinex",
                lambda exchange: (
                    VerifiedDigiFinexOrderBookProvider(
                        exchange
                    )
                ),
            )

        self._registry = registry

    def build(self, exchange):
        if exchange is None:
            raise ValueError("exchange is required")

        exchange_id = str(
            getattr(
                exchange,
                "id",
                "",
            )
            or ""
        ).strip().lower()

        provider = self._registry.build(
            exchange_id,
            exchange,
        )

        if provider is not None:
            return provider

        return LiveOrderBookSnapshotEngine(
            exchange
        )
