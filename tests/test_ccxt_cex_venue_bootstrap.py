import pytest

from core.ccxt_cex_venue_bootstrap import (
    CCXTCEXVenueBootstrap,
)
from core.configurable_cex_venue_registry import (
    ConfigurableCEXVenueRegistry,
)


class FakeExchange:
    def __init__(self, config=None):
        self.config = config or {}


class FakeCCXT:
    kraken = FakeExchange
    kucoin = FakeExchange


def test_registers_supported_ccxt_venues():
    registry = ConfigurableCEXVenueRegistry()
    bootstrap = CCXTCEXVenueBootstrap(FakeCCXT)

    bootstrap.register_venues(
        registry=registry,
        exchange_ids=["kraken", "kucoin"],
    )

    assert registry.enabled_exchange_ids() == [
        "kraken",
        "kucoin",
    ]


def test_registered_factory_creates_exchange_instance():
    registry = ConfigurableCEXVenueRegistry()
    bootstrap = CCXTCEXVenueBootstrap(FakeCCXT)

    bootstrap.register_venues(
        registry=registry,
        exchange_ids=["kraken"],
    )

    exchange = registry.create("kraken")

    assert isinstance(exchange, FakeExchange)


def test_rejects_unsupported_ccxt_exchange():
    registry = ConfigurableCEXVenueRegistry()
    bootstrap = CCXTCEXVenueBootstrap(FakeCCXT)

    with pytest.raises(ValueError, match="ccxt exchange not available"):
        bootstrap.register_venues(
            registry=registry,
            exchange_ids=["unknown"],
        )


def test_factory_enables_ccxt_rate_limit():
    registry = ConfigurableCEXVenueRegistry()
    bootstrap = CCXTCEXVenueBootstrap(FakeCCXT)

    bootstrap.register_venues(
        registry=registry,
        exchange_ids=["kraken"],
    )

    exchange = registry.create("kraken")

    assert exchange.config["enableRateLimit"] is True
