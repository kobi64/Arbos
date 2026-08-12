from core.live_market_event_dispatcher import (
    LiveMarketEventDispatcher,
)
from core.live_market_route_work_queue import (
    LiveMarketRouteWorkQueue,
)
from core.shared_live_market_data_cache import (
    SharedLiveMarketDataCache,
)


class CacheDispatchBridge:
    def __init__(
        self,
        cache,
        dispatcher,
    ):
        self._cache = cache
        self._dispatcher = dispatcher

    def publish(self, snapshot):
        result = self._cache.update(
            snapshot
        )

        if result.get("updated") is not True:
            return {
                **result,
                "dispatched": False,
            }

        dispatch = self._dispatcher.dispatch({
            "exchange_id": snapshot[
                "exchange_id"
            ],
            "symbol": snapshot[
                "symbol"
            ],
            "sequence": snapshot.get(
                "sequence"
            ),
            "priority": snapshot.get(
                "priority",
                0.0,
            ),
        })

        return {
            **result,
            "dispatched": True,
            "dispatch": dispatch,
        }


def snapshot(
    sequence,
    bid,
    ask,
):
    return {
        "exchange_id": "kucoin",
        "symbol": "BTC/USDT",
        "sequence": sequence,
        "timestamp": float(sequence),
        "bid": bid,
        "ask": ask,
    }


def test_accepted_snapshot_dispatches_affected_route():
    queue = LiveMarketRouteWorkQueue(
        max_queue_size=100
    )

    dispatcher = LiveMarketEventDispatcher(
        work_queue=queue
    )

    dispatcher.register_route(
        route_id="R-BTC",
        markets=[
            ("kucoin", "BTC/USDT"),
        ],
    )

    bridge = CacheDispatchBridge(
        cache=SharedLiveMarketDataCache(),
        dispatcher=dispatcher,
    )

    result = bridge.publish(
        snapshot(
            sequence=100,
            bid=100.0,
            ask=101.0,
        )
    )

    assert result["updated"] is True
    assert result["dispatched"] is True
    assert queue.pending_count() == 1

    work = queue.dequeue()

    assert work["route_id"] == "R-BTC"
    assert work["sequence"] == 100


def test_stale_snapshot_does_not_dispatch_work():
    queue = LiveMarketRouteWorkQueue(
        max_queue_size=100
    )

    dispatcher = LiveMarketEventDispatcher(
        work_queue=queue
    )

    dispatcher.register_route(
        route_id="R-BTC",
        markets=[
            ("kucoin", "BTC/USDT"),
        ],
    )

    bridge = CacheDispatchBridge(
        cache=SharedLiveMarketDataCache(),
        dispatcher=dispatcher,
    )

    bridge.publish(
        snapshot(
            sequence=105,
            bid=100.0,
            ask=101.0,
        )
    )

    queue.dequeue()

    result = bridge.publish(
        snapshot(
            sequence=104,
            bid=99.0,
            ask=100.0,
        )
    )

    assert result["updated"] is False
    assert result["dispatched"] is False
    assert result["reason"] == (
        "stale_market_sequence"
    )
    assert queue.pending_count() == 0


def test_duplicate_snapshot_does_not_dispatch_work():
    queue = LiveMarketRouteWorkQueue(
        max_queue_size=100
    )

    dispatcher = LiveMarketEventDispatcher(
        work_queue=queue
    )

    dispatcher.register_route(
        route_id="R-BTC",
        markets=[
            ("kucoin", "BTC/USDT"),
        ],
    )

    bridge = CacheDispatchBridge(
        cache=SharedLiveMarketDataCache(),
        dispatcher=dispatcher,
    )

    bridge.publish(
        snapshot(
            sequence=200,
            bid=100.0,
            ask=101.0,
        )
    )

    queue.dequeue()

    result = bridge.publish(
        snapshot(
            sequence=200,
            bid=101.0,
            ask=102.0,
        )
    )

    assert result["updated"] is False
    assert result["dispatched"] is False
    assert result["reason"] == (
        "duplicate_market_sequence"
    )
    assert queue.pending_count() == 0


def test_newer_snapshots_coalesce_to_latest_route_work():
    queue = LiveMarketRouteWorkQueue(
        max_queue_size=100
    )

    dispatcher = LiveMarketEventDispatcher(
        work_queue=queue
    )

    dispatcher.register_route(
        route_id="R-BTC",
        markets=[
            ("kucoin", "BTC/USDT"),
        ],
    )

    bridge = CacheDispatchBridge(
        cache=SharedLiveMarketDataCache(),
        dispatcher=dispatcher,
    )

    bridge.publish(
        snapshot(
            sequence=300,
            bid=100.0,
            ask=101.0,
        )
    )

    bridge.publish(
        snapshot(
            sequence=301,
            bid=101.0,
            ask=102.0,
        )
    )

    bridge.publish(
        snapshot(
            sequence=302,
            bid=102.0,
            ask=103.0,
        )
    )

    assert queue.pending_count() == 1

    work = queue.dequeue()

    assert work["sequence"] == 302
