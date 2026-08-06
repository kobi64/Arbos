import pytest

from core.configurable_cex_venue_registry import (
    ConfigurableCEXVenueRegistry,
)


class FakeExchange:
    def __init__(self, exchange_id):
        self.id = exchange_id


def kraken_factory():
    return FakeExchange("kraken")


def kucoin_factory():
    return FakeExchange("kucoin")


def test_registers_and_creates_enabled_venue():
    registry = ConfigurableCEXVenueRegistry()

    registry.register(
        exchange_id="kraken",
        factory=kraken_factory,
        enabled=True,
    )

    exchange = registry.create("kraken")

    assert exchange.id == "kraken"


def test_lists_only_enabled_venues_by_default():
    registry = ConfigurableCEXVenueRegistry()

    registry.register("kraken", kraken_factory, enabled=True)
    registry.register("kucoin", kucoin_factory, enabled=False)

    assert registry.enabled_exchange_ids() == ["kraken"]


def test_disabled_venue_cannot_be_created():
    registry = ConfigurableCEXVenueRegistry()

    registry.register("kucoin", kucoin_factory, enabled=False)

    with pytest.raises(ValueError, match="venue is disabled"):
        registry.create("kucoin")


def test_unknown_venue_is_rejected():
    registry = ConfigurableCEXVenueRegistry()

    with pytest.raises(ValueError, match="venue not registered"):
        registry.create("unknown")


def test_can_enable_and_disable_registered_venue():
    registry = ConfigurableCEXVenueRegistry()

    registry.register("kraken", kraken_factory, enabled=False)

    registry.set_enabled("kraken", True)
    assert registry.enabled_exchange_ids() == ["kraken"]

    registry.set_enabled("kraken", False)
    assert registry.enabled_exchange_ids() == []
