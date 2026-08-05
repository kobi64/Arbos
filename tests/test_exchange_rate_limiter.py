import pytest

from core.exchange_rate_limiter import ExchangeRateLimiter


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
def limiter(clock):
    return ExchangeRateLimiter(
        max_requests=3,
        window_seconds=10,
        clock=clock.now,
    )


def test_allows_requests_within_budget(limiter):
    first = limiter.allow_request("kraken")
    second = limiter.allow_request("kraken")
    third = limiter.allow_request("kraken")

    assert first["allowed"] is True
    assert second["allowed"] is True
    assert third["allowed"] is True
    assert third["remaining_requests"] == 0


def test_blocks_request_after_budget_exhausted(limiter):
    limiter.allow_request("kraken")
    limiter.allow_request("kraken")
    limiter.allow_request("kraken")

    result = limiter.allow_request("kraken")

    assert result["allowed"] is False
    assert result["reason"] == "rate_limit_reached"
    assert result["retry_after_seconds"] == 10.0


def test_resets_budget_after_window_expires(limiter, clock):
    limiter.allow_request("kraken")
    limiter.allow_request("kraken")
    limiter.allow_request("kraken")
    clock.advance(10)

    result = limiter.allow_request("kraken")

    assert result["allowed"] is True
    assert result["remaining_requests"] == 2


def test_tracks_exchange_budgets_independently(limiter):
    limiter.allow_request("kraken")
    limiter.allow_request("kraken")
    limiter.allow_request("kraken")

    result = limiter.allow_request("coinbase")

    assert result["allowed"] is True
    assert result["remaining_requests"] == 2


def test_invalid_max_requests_is_rejected(clock):
    with pytest.raises(ValueError, match="max_requests must be positive"):
        ExchangeRateLimiter(
            max_requests=0,
            window_seconds=10,
            clock=clock.now,
        )


def test_negative_window_is_rejected(clock):
    with pytest.raises(ValueError, match="window_seconds cannot be negative"):
        ExchangeRateLimiter(
            max_requests=3,
            window_seconds=-1,
            clock=clock.now,
        )
