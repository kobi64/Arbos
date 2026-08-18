import pytest

from core.market_data_freshness_guard import (
    MarketDataFreshnessGuard,
)


class FakeClock:
    def __init__(self):
        self.value = 1000.0

    def now(self):
        return self.value

    def advance(self, seconds):
        self.value += seconds


@pytest.fixture
def clock():
    return FakeClock()


@pytest.fixture
def guard(clock):
    return MarketDataFreshnessGuard(
        max_age_seconds=5,
        clock=clock.now,
    )


def test_accepts_fresh_market_data(guard):
    result = guard.evaluate(
        symbol="BTC/USDT",
        timestamp=998.0,
    )

    assert result["fresh"] is True
    assert result["reason"] is None
    assert result["age_seconds"] == 2.0


def test_rejects_stale_market_data(guard):
    result = guard.evaluate(
        symbol="BTC/USDT",
        timestamp=990.0,
    )

    assert result["fresh"] is False
    assert result["reason"] == "market_data_stale"


def test_rejects_market_data_at_age_boundary(guard):
    result = guard.evaluate(
        symbol="BTC/USDT",
        timestamp=995.0,
    )

    assert result["fresh"] is False
    assert result["age_seconds"] == 5.0


def test_rejects_future_dated_market_data(guard):
    result = guard.evaluate(
        symbol="BTC/USDT",
        timestamp=1001.0,
    )

    assert result["fresh"] is False
    assert (
        result["reason"]
        == "market_data_timestamp_in_future"
    )
    assert result["age_seconds"] == -1.0



def test_missing_symbol_is_rejected(guard):
    with pytest.raises(ValueError, match="symbol is required"):
        guard.evaluate(
            symbol="",
            timestamp=998.0,
        )


def test_negative_max_age_is_rejected(clock):
    with pytest.raises(ValueError, match="max_age_seconds cannot be negative"):
        MarketDataFreshnessGuard(
            max_age_seconds=-1,
            clock=clock.now,
        )
