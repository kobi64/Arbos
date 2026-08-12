import pytest

from core.live_market_event_dispatcher import (
    LiveMarketEventDispatcher,
)


class FakeWorkQueue:
    def __init__(self):
        self.items = []

    def enqueue(self, request):
        self.items.append(
            dict(request)
        )

        return {
            "queued": True,
            "request_id": request[
                "request_id"
            ],
        }


def test_dispatches_only_routes_affected_by_market_update():
    queue = FakeWorkQueue()

    dispatcher = LiveMarketEventDispatcher(
        work_queue=queue
    )

    dispatcher.register_route(
        route_id="R-SOL-1",
        markets=[
            ("kucoin", "SOL/USDT"),
            ("kucoin", "SOL/BTC"),
            ("kucoin", "BTC/USDT"),
        ],
    )

    dispatcher.register_route(
        route_id="R-ETH-1",
        markets=[
            ("kucoin", "ETH/USDT"),
            ("kucoin", "ETH/BTC"),
            ("kucoin", "BTC/USDT"),
        ],
    )

    result = dispatcher.dispatch({
        "exchange_id": "kucoin",
        "symbol": "SOL/USDT",
        "sequence": 101,
        "priority": 5.0,
    })

    assert result[
        "affected_route_count"
    ] == 1

    assert result[
        "affected_route_ids"
    ] == [
        "R-SOL-1",
    ]

    assert len(queue.items) == 1

    assert queue.items[0][
        "route_id"
    ] == "R-SOL-1"


def test_shared_market_dispatches_all_dependent_routes():
    queue = FakeWorkQueue()

    dispatcher = LiveMarketEventDispatcher(
        work_queue=queue
    )

    dispatcher.register_route(
        route_id="R-SOL",
        markets=[
            ("kucoin", "SOL/USDT"),
            ("kucoin", "SOL/BTC"),
            ("kucoin", "BTC/USDT"),
        ],
    )

    dispatcher.register_route(
        route_id="R-ETH",
        markets=[
            ("kucoin", "ETH/USDT"),
            ("kucoin", "ETH/BTC"),
            ("kucoin", "BTC/USDT"),
        ],
    )

    result = dispatcher.dispatch({
        "exchange_id": "kucoin",
        "symbol": "BTC/USDT",
        "sequence": 102,
        "priority": 8.0,
    })

    assert set(
        result["affected_route_ids"]
    ) == {
        "R-SOL",
        "R-ETH",
    }

    assert len(queue.items) == 2


def test_same_route_is_not_queued_twice_for_single_event():
    queue = FakeWorkQueue()

    dispatcher = LiveMarketEventDispatcher(
        work_queue=queue
    )

    dispatcher.register_route(
        route_id="R1",
        markets=[
            ("kucoin", "BTC/USDT"),
            ("KUCOIN", "btc/usdt"),
        ],
    )

    result = dispatcher.dispatch({
        "exchange_id": "KUCOIN",
        "symbol": "btc/usdt",
        "sequence": 103,
        "priority": 3.0,
    })

    assert result[
        "affected_route_count"
    ] == 1

    assert len(queue.items) == 1


def test_event_priority_is_forwarded_to_route_work():
    queue = FakeWorkQueue()

    dispatcher = LiveMarketEventDispatcher(
        work_queue=queue
    )

    dispatcher.register_route(
        route_id="R1",
        markets=[
            ("gate", "XRP/USDT"),
        ],
    )

    dispatcher.dispatch({
        "exchange_id": "gate",
        "symbol": "XRP/USDT",
        "sequence": 104,
        "priority": 9.5,
    })

    assert queue.items[0][
        "priority"
    ] == 9.5


def test_unrelated_market_creates_no_work():
    queue = FakeWorkQueue()

    dispatcher = LiveMarketEventDispatcher(
        work_queue=queue
    )

    dispatcher.register_route(
        route_id="R1",
        markets=[
            ("kucoin", "SOL/USDT"),
        ],
    )

    result = dispatcher.dispatch({
        "exchange_id": "gate",
        "symbol": "DOGE/USDT",
        "sequence": 105,
        "priority": 1.0,
    })

    assert result[
        "affected_route_count"
    ] == 0

    assert queue.items == []


def test_requires_exchange_and_symbol():
    dispatcher = LiveMarketEventDispatcher(
        work_queue=FakeWorkQueue()
    )

    with pytest.raises(
        ValueError,
        match="exchange_id is required",
    ):
        dispatcher.dispatch({
            "symbol": "BTC/USDT",
        })

    with pytest.raises(
        ValueError,
        match="symbol is required",
    ):
        dispatcher.dispatch({
            "exchange_id": "kucoin",
        })


def test_dispatcher_is_paper_safe_metadata_only():
    queue = FakeWorkQueue()

    dispatcher = LiveMarketEventDispatcher(
        work_queue=queue
    )

    dispatcher.register_route(
        route_id="R1",
        markets=[
            ("kucoin", "BTC/USDT"),
        ],
    )

    result = dispatcher.dispatch({
        "exchange_id": "kucoin",
        "symbol": "BTC/USDT",
        "sequence": 106,
    })

    assert result["paper_only"] is True
    assert (
        result["live_order_submitted"]
        is False
    )

    assert queue.items[0][
        "paper_only"
    ] is True

    assert queue.items[0][
        "live_order_submitted"
    ] is False
