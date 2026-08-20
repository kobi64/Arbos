import time

from core.htx_event_driven_market_feed import (
    HTXEventDrivenMarketFeed,
)
from core.live_market_data_intake_service import (
    LiveMarketDataIntakeService,
)
from core.live_market_event_dispatcher import (
    LiveMarketEventDispatcher,
)
from core.live_market_route_work_queue import (
    LiveMarketRouteWorkQueue,
)
from core.route_dependency_registry import (
    RouteDependencyRegistry,
)
from core.shared_live_market_data_cache import (
    SharedLiveMarketDataCache,
)


class FakeNativeFeed:
    pass


class FakeRestClient:
    def fetch_order_book(
        self,
        symbol,
        limit=20,
    ):
        return {
            "fetch_complete": True,
            "symbol": symbol,
            "bids": [
                [100.0, 5.0],
            ],
            "asks": [
                [101.0, 6.0],
            ],
            "timestamp": time.time(),
            "reason": None,
        }


class FailedRestClient:
    def fetch_order_book(
        self,
        symbol,
        limit=20,
    ):
        return {
            "fetch_complete": False,
            "symbol": symbol,
            "bids": [],
            "asks": [],
            "reason": "unavailable",
        }


def build_intake():
    registry = (
        RouteDependencyRegistry()
    )

    registry.register({
        "route_id": "R1",
        "exchange_id": "htx",
        "legs": [
            {
                "exchange_id": "htx",
                "symbol": "BTC/USDT",
                "side": "buy",
            },
        ],
    })

    queue = (
        LiveMarketRouteWorkQueue(
            max_queue_size=100
        )
    )

    dispatcher = (
        LiveMarketEventDispatcher(
            work_queue=queue,
            route_registry=registry,
        )
    )

    cache = (
        SharedLiveMarketDataCache()
    )

    intake = (
        LiveMarketDataIntakeService(
            cache=cache,
            dispatcher=dispatcher,
        )
    )

    return (
        intake,
        cache,
        queue,
    )


def test_native_bbo_enters_shared_cache():
    (
        intake,
        cache,
        queue,
    ) = build_intake()

    feed = (
        HTXEventDrivenMarketFeed(
            intake_service=intake,
            native_feed=FakeNativeFeed(),
            rest_client=FakeRestClient(),
        )
    )

    feed.submit_bbo({
        "symbol": "BTC/USDT",
        "best_bid": 100.0,
        "best_ask": 101.0,
        "bid_size": 5.0,
        "ask_size": 6.0,
        "timestamp": time.time(),
        "sequence": 10,
    })

    result = cache.get_with_freshness(
        "htx",
        "BTC/USDT",
    )

    snapshot = result["snapshot"]

    assert snapshot["bid"] == 100.0
    assert snapshot["ask"] == 101.0

    assert (
        snapshot[
            "market_data_source"
        ]
        == "HTX_NATIVE_BBO"
    )

    assert queue.pending_count() == 1


def test_native_update_dispatches_only_affected_route():
    (
        intake,
        cache,
        queue,
    ) = build_intake()

    feed = (
        HTXEventDrivenMarketFeed(
            intake_service=intake,
            native_feed=FakeNativeFeed(),
            rest_client=FakeRestClient(),
        )
    )

    feed.submit_bbo({
        "symbol": "ETH/USDT",
        "best_bid": 200.0,
        "best_ask": 201.0,
        "timestamp": time.time(),
        "sequence": 20,
    })

    assert queue.pending_count() == 0

    feed.submit_bbo({
        "symbol": "BTC/USDT",
        "best_bid": 100.0,
        "best_ask": 101.0,
        "timestamp": time.time(),
        "sequence": 21,
    })

    assert queue.pending_count() == 1


def test_rest_bootstrap_populates_cache():
    (
        intake,
        cache,
        queue,
    ) = build_intake()

    feed = (
        HTXEventDrivenMarketFeed(
            intake_service=intake,
            native_feed=FakeNativeFeed(),
            rest_client=FakeRestClient(),
        )
    )

    result = feed.bootstrap_symbol(
        "BTC/USDT"
    )

    assert result["submitted"] is True

    cached = cache.get_with_freshness(
        "htx",
        "BTC/USDT",
    )

    assert (
        cached["snapshot"][
            "market_data_source"
        ]
        == "HTX_REST_DEPTH_BOOTSTRAP"
    )

    assert queue.pending_count() == 1


def test_rest_failure_does_not_publish_bad_snapshot():
    (
        intake,
        cache,
        queue,
    ) = build_intake()

    feed = (
        HTXEventDrivenMarketFeed(
            intake_service=intake,
            native_feed=FakeNativeFeed(),
            rest_client=FailedRestClient(),
        )
    )

    result = feed.bootstrap_symbol(
        "BTC/USDT"
    )

    assert result["submitted"] is False

    assert queue.pending_count() == 0


def test_paper_only_safety_flags_preserved():
    (
        intake,
        cache,
        queue,
    ) = build_intake()

    feed = (
        HTXEventDrivenMarketFeed(
            intake_service=intake,
            native_feed=FakeNativeFeed(),
            rest_client=FakeRestClient(),
        )
    )

    feed.submit_bbo({
        "symbol": "BTC/USDT",
        "best_bid": 100.0,
        "best_ask": 101.0,
        "timestamp": time.time(),
    })

    cached = cache.get_with_freshness(
        "htx",
        "BTC/USDT",
    )

    snapshot = cached["snapshot"]

    assert snapshot["paper_only"] is True
    assert (
        snapshot["live_order_submitted"]
        is False
    )
