"""
ArbOS™
EX-254
Broad Public Paper Scan Application

Production composition root for the broad public paper scanner.

Wires:
- public CCXT exchange bootstrap
- live coin universe selector
- production multi-path pipeline factory
- production multi-path input preparer
- deduplicated unified public paper scanner
- broad public paper scan coordinator

Public market data / paper execution only.
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
from core.broad_public_paper_scan_coordinator import (
    BroadPublicPaperScanCoordinator,
)


class BroadPublicPaperScanApplication:
    def __init__(
        self,
        ccxt_module,
        universe_selector=None,
        pipeline_factory=None,
        input_preparer_factory=None,
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

        self._pipeline_factory = (
            pipeline_factory
            if pipeline_factory is not None
            else PublicLiveMultiPathPipelineFactory()
        )

        self._input_preparer_factory = (
            input_preparer_factory
            if input_preparer_factory is not None
            else PublicLiveMultiPathInputPreparer
        )

        self._scanner = (
            DeduplicatedUnifiedPublicPaperScanner(
                bootstrap=self._bootstrap,
                pipeline_factory=(
                    self._pipeline_factory
                ),
                input_preparer_factory=(
                    self._input_preparer_factory
                ),
            )
        )

        self._coordinator = (
            BroadPublicPaperScanCoordinator(
                bootstrap=self._bootstrap,
                universe_selector=(
                    self._universe_selector
                ),
                scanner=self._scanner,
            )
        )

    def run(
        self,
        exchange_ids,
        fee_rates,
        starting_usdt_value,
        max_slippage_percent,
        coin_limit=100,
    ):
        result = self._coordinator.run(
            exchange_ids=exchange_ids,
            fee_rates=fee_rates,
            starting_usdt_value=(
                starting_usdt_value
            ),
            max_slippage_percent=(
                max_slippage_percent
            ),
            coin_limit=coin_limit,
        )

        return {
            **result,
            "production_wiring": True,
            "paper_only": True,
            "live_order_submitted": False,
        }
