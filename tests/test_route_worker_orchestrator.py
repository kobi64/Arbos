import pytest

from core.route_worker_orchestrator import (
    RouteWorkerOrchestrator,
)
from core.route_dependency_registry import (
    RouteDependencyRegistry,
)
from core.live_market_route_work_queue import (
    LiveMarketRouteWorkQueue,
)


class FakeCache:
    pass


class FakeWorker:
    def __init__(
        self,
        work_queue,
        market_cache,
        route_registry,
    ):
        self.work_queue = work_queue
        self.market_cache = market_cache
        self.route_registry = route_registry
        self.processed = []

    def process_next(self):
        item = self.work_queue.dequeue()

        if item is None:
            return None

        self.processed.append(
            dict(item)
        )

        return {
            "processed": True,
            "route_id": item["route_id"],
        }


def sample_route(
    route_id="R1",
):
    return {
        "route_id": route_id,
        "exchange_id": "kucoin",
        "starting_value": 100.0,
        "fee_rate": 0.001,
        "max_slippage_percent": 0.5,
        "legs": [
            {
                "symbol": "ETH/USDT",
                "side": "buy",
            },
            {
                "symbol": "ETH/BTC",
                "side": "sell",
            },
            {
                "symbol": "BTC/USDT",
                "side": "sell",
            },
        ],
    }


def test_orchestrator_registers_route_once_in_shared_registry():
    registry = RouteDependencyRegistry()

    orchestrator = RouteWorkerOrchestrator(
        market_cache=FakeCache(),
        route_registry=registry,
        max_queue_size=100,
        worker_factory=FakeWorker,
    )

    result = orchestrator.register_route(
        sample_route()
    )

    assert result["registered"] is True
    assert registry.route_count() == 1

    assert orchestrator.dispatcher.routes_for_market(
        exchange_id="kucoin",
        symbol="BTC/USDT",
    ) == [
        "R1",
    ]


def test_dispatch_and_worker_share_same_registry():
    registry = RouteDependencyRegistry()

    orchestrator = RouteWorkerOrchestrator(
        market_cache=FakeCache(),
        route_registry=registry,
        max_queue_size=100,
        worker_factory=FakeWorker,
    )

    orchestrator.register_route(
        sample_route()
    )

    orchestrator.dispatch({
        "exchange_id": "kucoin",
        "symbol": "BTC/USDT",
        "sequence": 100,
        "priority": 5.0,
    })

    result = orchestrator.process_next()

    assert result["processed"] is True
    assert result["route_id"] == "R1"

    assert (
        orchestrator.worker.route_registry
        is registry
    )


def test_newer_market_event_coalesces_before_worker_processing():
    orchestrator = RouteWorkerOrchestrator(
        market_cache=FakeCache(),
        max_queue_size=100,
        worker_factory=FakeWorker,
    )

    orchestrator.register_route(
        sample_route()
    )

    orchestrator.dispatch({
        "exchange_id": "kucoin",
        "symbol": "BTC/USDT",
        "sequence": 100,
        "priority": 1.0,
    })

    orchestrator.dispatch({
        "exchange_id": "kucoin",
        "symbol": "BTC/USDT",
        "sequence": 101,
        "priority": 5.0,
    })

    assert orchestrator.pending_count() == 1

    orchestrator.process_next()

    assert (
        orchestrator.worker.processed[0][
            "sequence"
        ]
        == 101
    )


def test_process_until_empty_drains_available_work():
    orchestrator = RouteWorkerOrchestrator(
        market_cache=FakeCache(),
        max_queue_size=100,
        worker_factory=FakeWorker,
    )

    orchestrator.register_route(
        sample_route("R1")
    )

    orchestrator.register_route(
        {
            **sample_route("R2"),
            "legs": [
                {
                    "symbol": "SOL/USDT",
                    "side": "buy",
                },
                {
                    "symbol": "SOL/BTC",
                    "side": "sell",
                },
                {
                    "symbol": "BTC/USDT",
                    "side": "sell",
                },
            ],
        }
    )

    orchestrator.dispatch({
        "exchange_id": "kucoin",
        "symbol": "BTC/USDT",
        "sequence": 200,
        "priority": 1.0,
    })

    result = orchestrator.process_until_empty()

    assert result["processed_count"] == 2
    assert orchestrator.pending_count() == 0


def test_defaults_to_internal_registry_and_queue():
    orchestrator = RouteWorkerOrchestrator(
        market_cache=FakeCache(),
        max_queue_size=10,
        worker_factory=FakeWorker,
    )

    assert isinstance(
        orchestrator.route_registry,
        RouteDependencyRegistry,
    )

    assert isinstance(
        orchestrator.work_queue,
        LiveMarketRouteWorkQueue,
    )


def test_required_dependencies_are_validated():
    with pytest.raises(
        ValueError,
        match="market_cache is required",
    ):
        RouteWorkerOrchestrator(
            market_cache=None,
            max_queue_size=10,
            worker_factory=FakeWorker,
        )

    with pytest.raises(
        ValueError,
        match="worker_factory is required",
    ):
        RouteWorkerOrchestrator(
            market_cache=FakeCache(),
            max_queue_size=10,
            worker_factory=None,
        )
