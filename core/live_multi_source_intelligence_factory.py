"""
ArbOS™
EX-215
Live Multi-Source Intelligence Factory

Builds the real public external-intelligence stack:

CoinMarketGap
Sharpe Spot Transfer
Finder

All three sources share:
- one signal intake
- one correlator
- one source-performance tracker
- one generic normalizer

The resulting coordinators are combined by the
EX-214 Multi-Source External Intelligence Orchestrator
and wrapped by the EX-215 live cycle.

Paper-safe only.
No live orders.
"""

from core.coinmarketgap_api_client import (
    CoinMarketGapAPIClient,
)
from core.coinmarketgap_arbitrage_adapter import (
    CoinMarketGapArbitrageAdapter,
)
from core.coinmarketgap_external_intelligence_coordinator import (
    CoinMarketGapExternalIntelligenceCoordinator,
)
from core.sharpe_spot_transfer_api_client import (
    SharpeSpotTransferAPIClient,
)
from core.sharpe_spot_transfer_adapter import (
    SharpeSpotTransferAdapter,
)
from core.sharpe_external_intelligence_coordinator import (
    SharpeExternalIntelligenceCoordinator,
)
from core.finder_spot_intelligence_api_client import (
    FinderSpotIntelligenceAPIClient,
)
from core.finder_spot_intelligence_adapter import (
    FinderSpotIntelligenceAdapter,
)
from core.finder_external_intelligence_coordinator import (
    FinderExternalIntelligenceCoordinator,
)
from core.external_arbitrage_signal_normalizer import (
    ExternalArbitrageSignalNormalizer,
)
from core.external_arbitrage_signal_intake import (
    ExternalArbitrageSignalIntake,
)
from core.external_arbitrage_signal_correlator import (
    ExternalArbitrageSignalCorrelator,
)
from core.external_arbitrage_source_performance_tracker import (
    ExternalArbitrageSourcePerformanceTracker,
)
from core.multi_source_external_intelligence_orchestrator import (
    MultiSourceExternalIntelligenceOrchestrator,
)
from core.live_multi_source_intelligence_cycle import (
    LiveMultiSourceIntelligenceCycle,
)


class LiveMultiSourceIntelligenceFactory:
    def build_orchestrator(
        self,
        tracker=None,
        correlator=None,
    ):
        tracker = (
            tracker
            if tracker is not None
            else ExternalArbitrageSourcePerformanceTracker()
        )

        correlator = (
            correlator
            if correlator is not None
            else ExternalArbitrageSignalCorrelator()
        )

        normalizer = (
            ExternalArbitrageSignalNormalizer()
        )

        intake = (
            ExternalArbitrageSignalIntake()
        )

        coinmarketgap = (
            CoinMarketGapExternalIntelligenceCoordinator(
                client=CoinMarketGapAPIClient(),
                adapter=CoinMarketGapArbitrageAdapter(),
                normalizer=normalizer,
                intake=intake,
                correlator=correlator,
                tracker=tracker,
            )
        )

        sharpe = (
            SharpeExternalIntelligenceCoordinator(
                client=SharpeSpotTransferAPIClient(),
                adapter=SharpeSpotTransferAdapter(),
                normalizer=normalizer,
                intake=intake,
                correlator=correlator,
                tracker=tracker,
            )
        )

        finder = (
            FinderExternalIntelligenceCoordinator(
                client=FinderSpotIntelligenceAPIClient(),
                adapter=FinderSpotIntelligenceAdapter(),
                normalizer=normalizer,
                intake=intake,
                correlator=correlator,
                tracker=tracker,
            )
        )

        return (
            MultiSourceExternalIntelligenceOrchestrator(
                coordinators={
                    "coinmarketgap": coinmarketgap,
                    "sharpe": sharpe,
                    "finder": finder,
                }
            )
        )

    def build(
        self,
        tracker=None,
        correlator=None,
        clock=None,
    ):
        orchestrator = (
            self.build_orchestrator(
                tracker=tracker,
                correlator=correlator,
            )
        )

        return LiveMultiSourceIntelligenceCycle(
            orchestrator=orchestrator,
            clock=clock,
        )
