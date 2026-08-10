"""
ArbOS™
EX-181 / EX-182
Verified DigiFinex Order Book Provider

DigiFinex-specific composition of the exchange-agnostic
verified native market fallback infrastructure.

Public market data / paper valuation only.
No authentication.
No transfers.
No live orders.
"""

from exchanges.digifinex_native_market_source import (
    DigiFinexNativeMarketSource,
)
from exchanges.digifinex_native_order_book_source import (
    DigiFinexNativeOrderBookSource,
)
from exchanges.live_order_book_snapshot_engine import (
    LiveOrderBookSnapshotEngine,
)
from exchanges.verified_native_order_book_provider import (
    VerifiedNativeOrderBookProvider,
)
from exchanges.verified_raw_only_market_source import (
    VerifiedRawOnlyMarketSource,
)


class VerifiedDigiFinexOrderBookProvider:
    def __init__(self, exchange):
        if exchange is None:
            raise ValueError("exchange is required")

        verified_market_source = (
            VerifiedRawOnlyMarketSource(
                exchange_id="digifinex",
                exchange=exchange,
                native_market_source=(
                    DigiFinexNativeMarketSource(
                        exchange
                    )
                ),
            )
        )

        self._provider = (
            VerifiedNativeOrderBookProvider(
                exchange_id="digifinex",
                normal_provider=(
                    LiveOrderBookSnapshotEngine(
                        exchange
                    )
                ),
                native_provider=(
                    DigiFinexNativeOrderBookSource(
                        exchange
                    )
                ),
                verified_market_source=(
                    verified_market_source
                ),
            )
        )

    def snapshot(
        self,
        symbol,
        limit=None,
    ):
        return self._provider.snapshot(
            symbol,
            limit=limit,
        )
