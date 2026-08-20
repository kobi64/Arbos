"""
ArbOS™

EX-355
Event-Driven Public Feed Runtime

Composes the existing ArbOS persistent CCXT Pro public
market-data feed infrastructure with the shared-cache,
dependency-dispatch and worker architecture.

Architecture:

CCXT Pro WebSocket feeds
    -> CCXTProLiveOrderBookFeed
    -> LiveMarketDataIntakeService
    -> SharedLiveMarketDataCache
    -> LiveMarketEventDispatcher
    -> LiveMarketRouteWorkQueue
    -> ContinuousRouteWorkerPool

This module performs composition only.

Paper/public-data infrastructure only.
No authentication.
No transfers.
No live orders.
"""

from core.live_market_data_intake_service import (
    LiveMarketDataIntakeService,
)
from core.live_market_event_dispatcher import (
    LiveMarketEventDispatcher,
)
from core.ccxt_pro_live_order_book_feed import (
    CCXTProLiveOrderBookFeed,
)
from core.ccxt_pro_multi_symbol_feed_manager import (
    CCXTProMultiSymbolFeedManager,
)


class EventDrivenPublicFeedRuntime:
    def __init__(
        self,
        engine,
        exchanges,
        exchange_symbols,
        health_supervisors=None,
        backoff_policies=None,
    ):
        if engine is None:
            raise ValueError(
                "engine is required"
            )

        if not exchanges:
            raise ValueError(
                "exchanges are required"
            )

        if not exchange_symbols:
            raise ValueError(
                "exchange_symbols are required"
            )

        self._engine = engine
        self._exchanges = dict(
            exchanges
        )

        self._exchange_symbols = {
            str(exchange_id).strip().lower():
            self._normalize_symbols(symbols)
            for exchange_id, symbols
            in exchange_symbols.items()
        }

        self._health_supervisors = (
            health_supervisors
            or {}
        )

        self._backoff_policies = (
            backoff_policies
            or {}
        )

        self._managers = {}

        dispatcher = LiveMarketEventDispatcher(
            work_queue=engine.work_queue,
            route_registry=engine.route_registry,
        )

        self._intake = (
            LiveMarketDataIntakeService(
                cache=engine.market_cache,
                dispatcher=dispatcher,
            )
        )

        self._build_managers()

    @staticmethod
    def _normalize_symbols(symbols):
        result = []
        seen = set()

        for symbol in symbols or []:
            value = str(
                symbol
                or ""
            ).strip().upper()

            if not value:
                continue

            if value in seen:
                continue

            seen.add(value)
            result.append(value)

        return result

    def _build_managers(self):
        for exchange_id, exchange in (
            self._exchanges.items()
        ):
            normalized_id = str(
                exchange_id
                or ""
            ).strip().lower()

            symbols = (
                self._exchange_symbols.get(
                    normalized_id,
                    []
                )
            )

            if not symbols:
                continue

            feed = CCXTProLiveOrderBookFeed(
                exchange=exchange,
                intake_service=self._intake,
            )

            manager_kwargs = {
                "feed": feed,
                "exchange": exchange,
                "symbols": symbols,
            }

            supervisor = (
                self._health_supervisors.get(
                    normalized_id
                )
            )

            if supervisor is not None:
                manager_kwargs[
                    "health_supervisor"
                ] = supervisor

            backoff_policy = (
                self._backoff_policies.get(
                    normalized_id
                )
            )

            if backoff_policy is not None:
                manager_kwargs[
                    "backoff_policy"
                ] = backoff_policy

            self._managers[
                normalized_id
            ] = (
                CCXTProMultiSymbolFeedManager(
                    **manager_kwargs
                )
            )

    @property
    def managers(self):
        return dict(
            self._managers
        )

    @property
    def intake_service(self):
        return self._intake

    async def start(self):
        for manager in (
            self._managers.values()
        ):
            await manager.start()

        return {
            "started": True,
            "exchange_count": len(
                self._managers
            ),
            "symbol_count": sum(
                len(manager.symbols)
                for manager
                in self._managers.values()
            ),
            "paper_only": True,
            "live_order_submitted": False,
        }

    async def stop(self):
        for manager in (
            self._managers.values()
        ):
            await manager.stop()

        return {
            "stopped": True,
            "exchange_count": len(
                self._managers
            ),
            "paper_only": True,
            "live_order_submitted": False,
        }

    def process_pending(self):
        return (
            self._engine
            .process_pending()
        )

    def status(self):
        return {
            "exchange_count": len(
                self._managers
            ),
            "exchanges": sorted(
                self._managers
            ),
            "symbol_count": sum(
                len(manager.symbols)
                for manager
                in self._managers.values()
            ),
            "pending_route_count": (
                self._engine
                .work_queue
                .pending_count()
            ),
            "registered_route_count": (
                self._engine
                .route_registry
                .route_count()
            ),
            "paper_only": True,
            "live_order_submitted": False,
        }
