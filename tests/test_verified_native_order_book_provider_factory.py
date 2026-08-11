from exchanges.live_order_book_snapshot_engine import (
    LiveOrderBookSnapshotEngine,
)
from exchanges.verified_digifinex_order_book_provider import (
    VerifiedDigiFinexOrderBookProvider,
)
from exchanges.verified_native_order_book_provider_factory import (
    VerifiedNativeOrderBookProviderFactory,
)


class DigiFinexExchange:
    id = "digifinex"


class GateExchange:
    id = "gate"


class UnknownExchange:
    id = "unknown"


def test_builds_digifinex_verified_provider():
    exchange = DigiFinexExchange()

    provider = (
        VerifiedNativeOrderBookProviderFactory()
        .build(exchange)
    )

    assert isinstance(
        provider,
        VerifiedDigiFinexOrderBookProvider,
    )


def test_unregistered_exchange_uses_normal_ccxt_provider():
    exchange = GateExchange()

    provider = (
        VerifiedNativeOrderBookProviderFactory()
        .build(exchange)
    )

    assert isinstance(
        provider,
        LiveOrderBookSnapshotEngine,
    )


def test_unknown_exchange_uses_normal_ccxt_provider():
    exchange = UnknownExchange()

    provider = (
        VerifiedNativeOrderBookProviderFactory()
        .build(exchange)
    )

    assert isinstance(
        provider,
        LiveOrderBookSnapshotEngine,
    )


def test_exchange_without_id_uses_normal_provider():
    class NoIdExchange:
        pass

    exchange = NoIdExchange()

    provider = (
        VerifiedNativeOrderBookProviderFactory()
        .build(exchange)
    )

    assert isinstance(
        provider,
        LiveOrderBookSnapshotEngine,
    )


def test_missing_exchange_is_rejected():
    try:
        (
            VerifiedNativeOrderBookProviderFactory()
            .build(None)
        )
        assert False
    except ValueError as exc:
        assert str(exc) == "exchange is required"


def test_custom_registry_can_add_exchange_without_factory_change():
    from exchanges.native_fallback_exchange_registry import (
        NativeFallbackExchangeRegistry,
    )

    class CustomProvider:
        pass

    class GateExchange:
        id = "gate"

    registry = NativeFallbackExchangeRegistry()

    registry.register(
        "gate",
        lambda exchange: CustomProvider(),
    )

    factory = VerifiedNativeOrderBookProviderFactory(
        registry=registry
    )

    provider = factory.build(
        GateExchange()
    )

    assert isinstance(
        provider,
        CustomProvider,
    )
