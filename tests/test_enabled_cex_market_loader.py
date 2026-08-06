import pytest

from core.enabled_cex_market_loader import (
    EnabledCEXMarketLoader,
)
from core.configurable_cex_venue_registry import (
    ConfigurableCEXVenueRegistry,
)


class FakeExchange:
    def __init__(self, exchange_id, markets=None, fail=False):
        self.id = exchange_id
        self._markets = markets or {}
        self._fail = fail

    def load_markets(self):
        if self._fail:
            raise RuntimeError("market load failed")
        return self._markets


def make_factory(exchange_id, markets=None, fail=False):
    def factory():
        return FakeExchange(
            exchange_id=exchange_id,
            markets=markets,
            fail=fail,
        )

    return factory


def test_loads_markets_for_all_enabled_venues():
    registry = ConfigurableCEXVenueRegistry()

    registry.register(
        "kraken",
        make_factory(
            "kraken",
            {"BTC/USDT": {"spot": True}},
        ),
    )
    registry.register(
        "kucoin",
        make_factory(
            "kucoin",
            {"ETH/USDT": {"spot": True}},
        ),
    )

    loader = EnabledCEXMarketLoader(registry)

    result = loader.load()

    assert set(result["markets"]) == {"kraken", "kucoin"}
    assert "BTC/USDT" in result["markets"]["kraken"]
    assert "ETH/USDT" in result["markets"]["kucoin"]


def test_does_not_load_disabled_venues():
    registry = ConfigurableCEXVenueRegistry()

    registry.register(
        "kraken",
        make_factory(
            "kraken",
            {"BTC/USDT": {"spot": True}},
        ),
        enabled=True,
    )
    registry.register(
        "kucoin",
        make_factory(
            "kucoin",
            {"ETH/USDT": {"spot": True}},
        ),
        enabled=False,
    )

    loader = EnabledCEXMarketLoader(registry)

    result = loader.load()

    assert set(result["markets"]) == {"kraken"}
    assert "kucoin" not in result["markets"]


def test_one_failed_venue_does_not_stop_other_market_loads():
    registry = ConfigurableCEXVenueRegistry()

    registry.register(
        "kraken",
        make_factory(
            "kraken",
            {"BTC/USDT": {"spot": True}},
        ),
    )
    registry.register(
        "broken",
        make_factory(
            "broken",
            fail=True,
        ),
    )

    loader = EnabledCEXMarketLoader(registry)

    result = loader.load()

    assert "kraken" in result["markets"]
    assert "broken" not in result["markets"]
    assert "broken" in result["failures"]
    assert result["failures"]["broken"]["reason"] == "market_load_failed"
