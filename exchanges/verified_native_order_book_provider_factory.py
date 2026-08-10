"""
ArbOS™
EX-182
Verified Native Order Book Provider Factory

Selects the appropriate public order-book provider for an exchange.

Registered exchanges may use a verified native fallback path.
Unregistered exchanges continue using the normal CCXT snapshot engine.

Public market data / paper valuation only.
No authentication.
No transfers.
No live orders.
"""

from exchanges.live_order_book_snapshot_engine import (
    LiveOrderBookSnapshotEngine,
)
from exchanges.verified_digifinex_order_book_provider import (
    VerifiedDigiFinexOrderBookProvider,
)


class VerifiedNativeOrderBookProviderFactory:
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

        if exchange_id == "digifinex":
            return (
                VerifiedDigiFinexOrderBookProvider(
                    exchange
                )
            )

        return LiveOrderBookSnapshotEngine(
            exchange
        )
