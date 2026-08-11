import pytest

from exchanges.native_fallback_exchange_registry import (
    NativeFallbackExchangeRegistry,
)


class FakeProvider:
    pass


def test_registers_and_builds_provider():
    registry = NativeFallbackExchangeRegistry()

    registry.register(
        "digifinex",
        lambda exchange: FakeProvider(),
    )

    provider = registry.build(
        "digifinex",
        object(),
    )

    assert isinstance(provider, FakeProvider)


def test_exchange_id_is_normalized():
    registry = NativeFallbackExchangeRegistry()

    registry.register(
        " DigiFinex ",
        lambda exchange: FakeProvider(),
    )

    assert registry.has("digifinex") is True
    assert registry.has("DIGIFINEX") is True


def test_unknown_exchange_returns_none():
    registry = NativeFallbackExchangeRegistry()

    assert registry.build(
        "gate",
        object(),
    ) is None


def test_duplicate_registration_replaces_builder():
    registry = NativeFallbackExchangeRegistry()

    registry.register(
        "exchange",
        lambda exchange: "first",
    )

    registry.register(
        "exchange",
        lambda exchange: "second",
    )

    assert registry.build(
        "exchange",
        object(),
    ) == "second"


def test_missing_exchange_id_is_rejected():
    registry = NativeFallbackExchangeRegistry()

    with pytest.raises(
        ValueError,
        match="exchange_id is required",
    ):
        registry.register(
            "",
            lambda exchange: FakeProvider(),
        )


def test_missing_builder_is_rejected():
    registry = NativeFallbackExchangeRegistry()

    with pytest.raises(
        ValueError,
        match="builder is required",
    ):
        registry.register(
            "digifinex",
            None,
        )
