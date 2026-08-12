from core.live_market_event_dispatcher import (
    LiveMarketEventDispatcher,
)
from core.live_market_route_work_queue import (
    LiveMarketRouteWorkQueue,
)


def test_rapid_market_updates_coalesce_to_latest_route_work():
    queue = LiveMarketRouteWorkQueue(
        max_queue_size=100
    )

    dispatcher = LiveMarketEventDispatcher(
        work_queue=queue
    )

    dispatcher.register_route(
        route_id="R-BTC-SOL",
        markets=[
            ("kucoin", "BTC/USDT"),
            ("kucoin", "SOL/BTC"),
            ("kucoin", "SOL/USDT"),
        ],
    )

    dispatcher.dispatch({
        "exchange_id": "kucoin",
        "symbol": "BTC/USDT",
        "sequence": 100,
        "priority": 1.0,
    })

    dispatcher.dispatch({
        "exchange_id": "kucoin",
        "symbol": "BTC/USDT",
        "sequence": 101,
        "priority": 2.0,
    })

    dispatcher.dispatch({
        "exchange_id": "kucoin",
        "symbol": "BTC/USDT",
        "sequence": 102,
        "priority": 3.0,
    })

    assert queue.pending_count() == 1

    work = queue.dequeue()

    assert work["route_id"] == (
        "R-BTC-SOL"
    )

    assert work["sequence"] == 102
    assert work["priority"] == 3.0


def test_shared_market_updates_keep_one_latest_item_per_route():
    queue = LiveMarketRouteWorkQueue(
        max_queue_size=100
    )

    dispatcher = LiveMarketEventDispatcher(
        work_queue=queue
    )

    dispatcher.register_route(
        route_id="R-SOL",
        markets=[
            ("kucoin", "BTC/USDT"),
            ("kucoin", "SOL/BTC"),
        ],
    )

    dispatcher.register_route(
        route_id="R-ETH",
        markets=[
            ("kucoin", "BTC/USDT"),
            ("kucoin", "ETH/BTC"),
        ],
    )

    dispatcher.dispatch({
        "exchange_id": "kucoin",
        "symbol": "BTC/USDT",
        "sequence": 200,
        "priority": 1.0,
    })

    dispatcher.dispatch({
        "exchange_id": "kucoin",
        "symbol": "BTC/USDT",
        "sequence": 201,
        "priority": 5.0,
    })

    assert queue.pending_count() == 2

    first = queue.dequeue()
    second = queue.dequeue()

    assert {
        first["route_id"],
        second["route_id"],
    } == {
        "R-SOL",
        "R-ETH",
    }

    assert first["sequence"] == 201
    assert second["sequence"] == 201


def test_unrelated_market_update_does_not_create_work():
    queue = LiveMarketRouteWorkQueue(
        max_queue_size=100
    )

    dispatcher = LiveMarketEventDispatcher(
        work_queue=queue
    )

    dispatcher.register_route(
        route_id="R1",
        markets=[
            ("kucoin", "ETH/USDT"),
        ],
    )

    dispatcher.dispatch({
        "exchange_id": "gate",
        "symbol": "DOGE/USDT",
        "sequence": 300,
    })

    assert queue.pending_count() == 0
