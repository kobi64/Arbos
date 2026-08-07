"""
ArbOS™
EX-142
Public Live Multi-Path Pipeline Factory
"""

from core.coin_first_multi_bridge_triangle_discovery import (
    CoinFirstMultiBridgeTriangleDiscovery,
)
from core.cross_exchange_route_candidate_generator import (
    CrossExchangeRouteCandidateGenerator,
)
from core.cross_exchange_route_valuation import (
    CrossExchangeRouteValuation,
)
from core.internal_multi_bridge_route_ranker import (
    InternalMultiBridgeRouteRanker,
)
from core.internal_multi_bridge_scan_coordinator import (
    InternalMultiBridgeScanCoordinator,
)
from core.live_multi_path_paper_scan import (
    LiveMultiPathPaperScan,
)
from core.multi_path_arbitrage_integration_coordinator import (
    MultiPathArbitrageIntegrationCoordinator,
)
from core.multi_path_arbitrage_route_evaluator import (
    MultiPathArbitrageRouteEvaluator,
)
from core.order_book_depth_aware_triangle_scanner import (
    OrderBookDepthAwareTriangleScanner,
)
from exchanges.live_order_book_snapshot_engine import (
    LiveOrderBookSnapshotEngine,
)
from exchanges.transfer_route_evaluation import (
    TransferRouteEvaluation,
)


class PublicLiveMultiPathPipelineFactory:
    def build(
        self,
        source_exchange,
        destination_exchange,
    ):
        source_order_books = LiveOrderBookSnapshotEngine(
            source_exchange
        )

        destination_order_books = (
            LiveOrderBookSnapshotEngine(
                destination_exchange
            )
        )

        source_route_scanner = (
            OrderBookDepthAwareTriangleScanner(
                source_order_books
            )
        )

        destination_route_scanner = (
            OrderBookDepthAwareTriangleScanner(
                destination_order_books
            )
        )

        internal_scanner = (
            InternalMultiBridgeScanCoordinator(
                discovery=(
                    CoinFirstMultiBridgeTriangleDiscovery()
                ),
                route_scanner=source_route_scanner,
                ranker=InternalMultiBridgeRouteRanker(),
            )
        )

        cross_exchange_generator = (
            CrossExchangeRouteCandidateGenerator(
                transfer_evaluator=TransferRouteEvaluation,
            )
        )

        cross_exchange_valuation = (
            CrossExchangeRouteValuation(
                destination_scanner=(
                    destination_route_scanner
                ),
            )
        )

        integration_coordinator = (
            MultiPathArbitrageIntegrationCoordinator(
                cross_exchange_generator=(
                    cross_exchange_generator
                ),
                cross_exchange_valuation=(
                    cross_exchange_valuation
                ),
                evaluator=(
                    MultiPathArbitrageRouteEvaluator()
                ),
            )
        )

        return LiveMultiPathPaperScan(
            internal_scanner=internal_scanner,
            integration_coordinator=(
                integration_coordinator
            ),
        )
