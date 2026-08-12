import pytest

from core.live_market_data_intake_service import (
    LiveMarketDataIntakeService,
)


class FakeCache:
    def __init__(self):
        self.calls = []
        self.mode = "updated"

    def update(self, snapshot):
        self.calls.append(
            dict(snapshot)
        )

        if self.mode == "stale":
            return {
                "updated": False,
                "reason": (
                    "stale_market_sequence"
                ),
            }

        if self.mode == "duplicate":
            return {
                "updated": False,
                "reason": (
                    "duplicate_market_sequence"
                ),
            }

        return {
            "updated": True,
            "reason": None,
            "exchange_id": (
                snapshot["exchange_id"]
            ),
            "symbol": snapshot["symbol"],
            "sequence": snapshot.get(
                "sequence"
            ),
        }


class FakeDispatcher:
    def __init__(self):
        self.calls = []

    def dispatch(self, event):
        self.calls.append(
            dict(event)
        )

        return {
            "affected_route_count": 2,
            "queued_route_count": 2,
            "paper_only": True,
            "live_order_submitted": False,
        }


def market_snapshot(
    sequence=100,
    priority=5.0,
):
    return {
        "exchange_id": "kucoin",
        "symbol": "BTC/USDT",
        "sequence": sequence,
        "timestamp": 1000.0,
        "bid": 100.0,
        "ask": 101.0,
        "priority": priority,
    }


def test_accepts_snapshot_updates_cache_and_dispatches():
    cache = FakeCache()
    dispatcher = FakeDispatcher()

    intake = LiveMarketDataIntakeService(
        cache=cache,
        dispatcher=dispatcher,
    )

    result = intake.submit(
        market_snapshot()
    )

    assert result["accepted"] is True
    assert result["updated"] is True
    assert result["dispatched"] is True

    assert len(cache.calls) == 1
    assert len(dispatcher.calls) == 1

    event = dispatcher.calls[0]

    assert event["exchange_id"] == "kucoin"
    assert event["symbol"] == "BTC/USDT"
    assert event["sequence"] == 100
    assert event["priority"] == 5.0


def test_stale_snapshot_is_rejected_without_dispatch():
    cache = FakeCache()
    cache.mode = "stale"

    dispatcher = FakeDispatcher()

    intake = LiveMarketDataIntakeService(
        cache=cache,
        dispatcher=dispatcher,
    )

    result = intake.submit(
        market_snapshot(
            sequence=99
        )
    )

    assert result["accepted"] is False
    assert result["updated"] is False
    assert result["dispatched"] is False
    assert result["reason"] == (
        "stale_market_sequence"
    )

    assert dispatcher.calls == []


def test_duplicate_snapshot_is_rejected_without_dispatch():
    cache = FakeCache()
    cache.mode = "duplicate"

    dispatcher = FakeDispatcher()

    intake = LiveMarketDataIntakeService(
        cache=cache,
        dispatcher=dispatcher,
    )

    result = intake.submit(
        market_snapshot()
    )

    assert result["accepted"] is False
    assert result["dispatched"] is False
    assert result["reason"] == (
        "duplicate_market_sequence"
    )

    assert dispatcher.calls == []


def test_priority_defaults_to_zero():
    cache = FakeCache()
    dispatcher = FakeDispatcher()

    intake = LiveMarketDataIntakeService(
        cache=cache,
        dispatcher=dispatcher,
    )

    snapshot = market_snapshot()
    snapshot.pop("priority")

    intake.submit(snapshot)

    assert dispatcher.calls[0][
        "priority"
    ] == 0.0


def test_statistics_track_received_accepted_rejected_and_dispatched():
    cache = FakeCache()
    dispatcher = FakeDispatcher()

    intake = LiveMarketDataIntakeService(
        cache=cache,
        dispatcher=dispatcher,
    )

    intake.submit(
        market_snapshot(
            sequence=100
        )
    )

    cache.mode = "stale"

    intake.submit(
        market_snapshot(
            sequence=99
        )
    )

    stats = intake.statistics()

    assert stats["received"] == 2
    assert stats["accepted"] == 1
    assert stats["rejected"] == 1
    assert stats["dispatched"] == 1


def test_missing_cache_is_rejected():
    with pytest.raises(
        ValueError,
        match="cache is required",
    ):
        LiveMarketDataIntakeService(
            cache=None,
            dispatcher=FakeDispatcher(),
        )


def test_missing_dispatcher_is_rejected():
    with pytest.raises(
        ValueError,
        match="dispatcher is required",
    ):
        LiveMarketDataIntakeService(
            cache=FakeCache(),
            dispatcher=None,
        )


def test_invalid_snapshot_updates_rejected_statistics():
    class RejectingCache:
        def update(self, snapshot):
            raise ValueError(
                "symbol is required"
            )

    intake = LiveMarketDataIntakeService(
        cache=RejectingCache(),
        dispatcher=FakeDispatcher(),
    )

    with pytest.raises(
        ValueError,
        match="symbol is required",
    ):
        intake.submit({
            "exchange_id": "kucoin",
        })

    stats = intake.statistics()

    assert stats["received"] == 1
    assert stats["accepted"] == 0
    assert stats["rejected"] == 1
    assert stats["dispatched"] == 0


def test_intake_result_is_paper_safe():
    intake = LiveMarketDataIntakeService(
        cache=FakeCache(),
        dispatcher=FakeDispatcher(),
    )

    result = intake.submit(
        market_snapshot()
    )

    assert result["paper_only"] is True
    assert (
        result["live_order_submitted"]
        is False
    )
