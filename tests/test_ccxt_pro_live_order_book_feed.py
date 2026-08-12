import asyncio

import pytest

from core.ccxt_pro_live_order_book_feed import (
    CCXTProLiveOrderBookFeed,
)


class FakeExchange:
    id = "kucoin"

    def __init__(self):
        self.calls = []
        self.books = []

    async def watch_order_book(
        self,
        symbol,
        limit=None,
    ):
        self.calls.append(
            (
                symbol,
                limit,
            )
        )

        if not self.books:
            raise RuntimeError(
                "no fake order book available"
            )

        return self.books.pop(0)


class FakeIntake:
    def __init__(self):
        self.snapshots = []

    def submit(self, snapshot):
        self.snapshots.append(
            dict(snapshot)
        )

        return {
            "accepted": True,
            "updated": True,
            "dispatched": True,
            "paper_only": True,
            "live_order_submitted": False,
        }


def book(
    bid,
    ask,
    nonce=None,
    timestamp=1000,
):
    return {
        "symbol": "BTC/USDT",
        "bids": [
            [bid, 2.0],
        ],
        "asks": [
            [ask, 3.0],
        ],
        "timestamp": timestamp,
        "datetime": None,
        "nonce": nonce,
    }


def test_watch_once_normalizes_and_submits_order_book():
    exchange = FakeExchange()

    exchange.books.append(
        book(
            bid=50000.0,
            ask=50010.0,
            nonce=777,
        )
    )

    intake = FakeIntake()

    feed = CCXTProLiveOrderBookFeed(
        exchange=exchange,
        intake_service=intake,
    )

    result = asyncio.run(
        feed.watch_once(
            symbol="BTC/USDT",
            limit=20,
        )
    )

    assert result["accepted"] is True
    assert exchange.calls == [
        (
            "BTC/USDT",
            20,
        )
    ]

    assert len(
        intake.snapshots
    ) == 1

    snapshot = intake.snapshots[0]

    assert snapshot[
        "exchange_id"
    ] == "kucoin"

    assert snapshot[
        "symbol"
    ] == "BTC/USDT"

    assert snapshot[
        "best_bid"
    ] == 50000.0

    assert snapshot[
        "best_ask"
    ] == 50010.0

    assert snapshot[
        "bids"
    ] == [
        [50000.0, 2.0],
    ]

    assert snapshot[
        "asks"
    ] == [
        [50010.0, 3.0],
    ]

    assert snapshot[
        "source_sequence"
    ] == 777

    assert snapshot[
        "sequence"
    ] == 1


def test_feed_assigns_monotonic_local_sequence():
    exchange = FakeExchange()

    exchange.books.extend([
        book(
            50000.0,
            50010.0,
            nonce=900,
        ),
        book(
            50001.0,
            50011.0,
            nonce=901,
        ),
        book(
            50002.0,
            50012.0,
            nonce=902,
        ),
    ])

    intake = FakeIntake()

    feed = CCXTProLiveOrderBookFeed(
        exchange=exchange,
        intake_service=intake,
    )

    for _ in range(3):
        asyncio.run(
            feed.watch_once(
                "BTC/USDT"
            )
        )

    assert [
        item["sequence"]
        for item in intake.snapshots
    ] == [
        1,
        2,
        3,
    ]

    assert [
        item["source_sequence"]
        for item in intake.snapshots
    ] == [
        900,
        901,
        902,
    ]


def test_symbol_is_normalized():
    exchange = FakeExchange()

    exchange.books.append(
        book(
            50000.0,
            50010.0,
        )
    )

    intake = FakeIntake()

    feed = CCXTProLiveOrderBookFeed(
        exchange=exchange,
        intake_service=intake,
    )

    asyncio.run(
        feed.watch_once(
            " btc/usdt "
        )
    )

    assert exchange.calls[0][0] == (
        "BTC/USDT"
    )

    assert intake.snapshots[0][
        "symbol"
    ] == "BTC/USDT"


def test_empty_order_book_is_rejected_before_intake():
    exchange = FakeExchange()

    exchange.books.append({
        "symbol": "BTC/USDT",
        "bids": [],
        "asks": [],
        "timestamp": 1000,
    })

    intake = FakeIntake()

    feed = CCXTProLiveOrderBookFeed(
        exchange=exchange,
        intake_service=intake,
    )

    with pytest.raises(
        ValueError,
        match="order book unavailable",
    ):
        asyncio.run(
            feed.watch_once(
                "BTC/USDT"
            )
        )

    assert intake.snapshots == []


def test_missing_timestamp_uses_clock():
    exchange = FakeExchange()

    data = book(
        50000.0,
        50010.0,
    )

    data["timestamp"] = None

    exchange.books.append(
        data
    )

    intake = FakeIntake()

    feed = CCXTProLiveOrderBookFeed(
        exchange=exchange,
        intake_service=intake,
        clock=lambda: 1234.5,
    )

    asyncio.run(
        feed.watch_once(
            "BTC/USDT"
        )
    )

    assert intake.snapshots[0][
        "timestamp"
    ] == 1234.5


def test_required_dependencies_are_validated():
    with pytest.raises(
        ValueError,
        match="exchange is required",
    ):
        CCXTProLiveOrderBookFeed(
            exchange=None,
            intake_service=FakeIntake(),
        )

    with pytest.raises(
        ValueError,
        match="intake_service is required",
    ):
        CCXTProLiveOrderBookFeed(
            exchange=FakeExchange(),
            intake_service=None,
        )


def test_feed_is_public_paper_safe():
    exchange = FakeExchange()

    exchange.books.append(
        book(
            50000.0,
            50010.0,
        )
    )

    intake = FakeIntake()

    feed = CCXTProLiveOrderBookFeed(
        exchange=exchange,
        intake_service=intake,
    )

    result = asyncio.run(
        feed.watch_once(
            "BTC/USDT"
        )
    )

    assert result[
        "paper_only"
    ] is True

    assert result[
        "live_order_submitted"
    ] is False

    assert intake.snapshots[0][
        "paper_only"
    ] is True

    assert intake.snapshots[0][
        "live_order_submitted"
    ] is False
