"""
ArbOS™
EX-184
Verified KuCoin Order Book Provider

KuCoin-specific composition of the exchange-agnostic
verified native fallback infrastructure.

Public market data / paper valuation only.
No authentication.
No transfers.
No live orders.
"""

from exchanges.kucoin_native_market_source import (
    KuCoinNativeMarketSource,
)
from exchanges.kucoin_native_order_book_source import (
    KuCoinNativeOrderBookSource,
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


class VerifiedKuCoinOrderBookProvider:
    def __init__(self, exchange):
        if exchange is None:
            raise ValueError("exchange is required")

        verified_market_source = (
            VerifiedRawOnlyMarketSource(
                exchange_id="kucoin",
                exchange=exchange,
                native_market_source=(
                    KuCoinNativeMarketSource(
                        exchange
                    )
                ),
            )
        )

        self._provider = (
            VerifiedNativeOrderBookProvider(
                exchange_id="kucoin",
                normal_provider=(
                    LiveOrderBookSnapshotEngine(
                        exchange
                    )
                ),
                native_provider=(
                    KuCoinNativeOrderBookSource(
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
