"""
ArbOS™

EX-352
100-Coin Public Paper Scan Application

Production composition root for a controlled 100-coin
public-market-data paper scan.

Sequence:
- create public CCXT exchanges
- discover liquid USDT spot universes
- require globally approved cross-exchange universe
- require verified feed capacity
- scan exactly the approved universe

Public data / paper execution only.
No authentication.
No transfers.
No live orders.
"""

from core.public_ccxt_exchange_bootstrap import (
    PublicCCXTExchangeBootstrap,
)
from core.live_coin_universe_selector import (
    LiveCoinUniverseSelector,
)
from core.public_live_multi_path_pipeline_factory import (
    PublicLiveMultiPathPipelineFactory,
)
from core.public_live_multi_path_input_preparer import (
    PublicLiveMultiPathInputPreparer,
)
from core.deduplicated_unified_public_paper_scanner import (
    DeduplicatedUnifiedPublicPaperScanner,
)
from core.exchange_subscription_capacity_profiles import (
    ExchangeSubscriptionCapacityProfiles,
)
from core.verified_production_feed_profiles import (
    VerifiedProductionFeedProfiles,
)
from core.hundred_coin_public_paper_scan_harness import (
    HundredCoinPublicPaperScanHarness,
)


class HundredCoinPublicPaperScanApplication:
    def __init__(
        self,
        ccxt_module,
        universe_selector=None,
        capacity_profiles=None,
    ):
        if ccxt_module is None:
            raise ValueError(
                "ccxt_module is required"
            )

        self._bootstrap = (
            PublicCCXTExchangeBootstrap(
                ccxt_module
            )
        )

        self._universe_selector = (
            universe_selector
            if universe_selector is not None
            else LiveCoinUniverseSelector()
        )

        pipeline_factory = (
            PublicLiveMultiPathPipelineFactory()
        )

        scanner = (
            DeduplicatedUnifiedPublicPaperScanner(
                bootstrap=self._bootstrap,
                pipeline_factory=(
                    pipeline_factory
                ),
                input_preparer_factory=(
                    PublicLiveMultiPathInputPreparer
                ),
            )
        )

        if capacity_profiles is None:
            capacity_profiles = (
                ExchangeSubscriptionCapacityProfiles()
            )

            (
                VerifiedProductionFeedProfiles()
                .register_all(
                    capacity_profiles
                )
            )

        self._capacity_profiles = (
            capacity_profiles
        )

        self._harness = (
            HundredCoinPublicPaperScanHarness(
                scanner=scanner,
                capacity_profiles=(
                    self._capacity_profiles
                ),
            )
        )

    def run(
        self,
        exchange_ids,
        fee_rates,
        starting_usdt_value,
        max_slippage_percent,
        requested_coin_count=100,
        discovery_limit=250,
        minimum_exchange_coverage=2,
    ):
        exchange_ids = [
            str(exchange_id)
            .strip()
            .lower()
            for exchange_id in (
                exchange_ids or []
            )
            if str(exchange_id).strip()
        ]

        exchange_ids = list(
            dict.fromkeys(
                exchange_ids
            )
        )

        if len(exchange_ids) < 2:
            raise ValueError(
                "at least two exchanges are required"
            )

        if discovery_limit <= 0:
            raise ValueError(
                "discovery_limit must be positive"
            )

        exchange_coin_assets = {}
        discovery = {}

        for exchange_id in exchange_ids:
            exchange = (
                self._bootstrap.create(
                    exchange_id
                )
            )

            markets = (
                exchange.load_markets()
            )

            try:
                tickers = (
                    exchange.fetch_tickers()
                )
            except Exception as exc:
                discovery[
                    exchange_id
                ] = {
                    "exchange_id": (
                        exchange_id
                    ),
                    "discovery_ready": False,
                    "reason": (
                        "ticker_discovery_failed"
                    ),
                    "error_type": (
                        type(exc).__name__
                    ),
                    "paper_only": True,
                    "live_order_submitted": False,
                }
                continue

            selection = (
                self._universe_selector.select(
                    exchange_id=(
                        exchange_id
                    ),
                    markets=markets,
                    tickers=tickers,
                    limit=(
                        discovery_limit
                    ),
                )
            )

            discovery[
                exchange_id
            ] = {
                **selection,
                "discovery_ready": True,
            }

            exchange_coin_assets[
                exchange_id
            ] = set(
                selection.get(
                    "coin_assets",
                    [],
                )
            )

        result = self._harness.run(
            exchange_coin_assets=(
                exchange_coin_assets
            ),
            fee_rates=fee_rates,
            starting_usdt_value=(
                starting_usdt_value
            ),
            max_slippage_percent=(
                max_slippage_percent
            ),
            requested_coin_count=(
                requested_coin_count
            ),
            minimum_exchange_coverage=(
                minimum_exchange_coverage
            ),
        )

        return {
            **result,
            "exchange_ids": exchange_ids,
            "discovery_limit": (
                discovery_limit
            ),
            "discovery": discovery,
            "production_wiring": True,
            "paper_only": True,
            "live_order_submitted": (
                result.get(
                    "live_order_submitted",
                    False,
                )
            ),
        }
