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


def test_builds_kucoin_verified_provider():
    from exchanges.verified_kucoin_order_book_provider import (
        VerifiedKuCoinOrderBookProvider,
    )

    class KuCoinExchange:
        id = "kucoin"

    provider = (
        VerifiedNativeOrderBookProviderFactory()
        .build(
            KuCoinExchange()
        )
    )

    assert isinstance(
        provider,
        VerifiedKuCoinOrderBookProvider,
    )


def test_builds_weex_native_provider():
    from exchanges.weex_native_order_book_provider import (
        WeexNativeOrderBookProvider,
    )
    from exchanges.native_fallback_exchange_registry import (
        NativeFallbackExchangeRegistry,
    )

    class WeexExchange:
        id = "weex"

    class FakeWeexBackend:
        def get_order_book(
            self,
            symbol,
            limit=200,
        ):
            return {
                "exchange": "weex",
                "available": True,
                "symbol": symbol,
                "best_bid": 1.0,
                "best_ask": 1.01,
                "bids": [
                    {
                        "price": 1.0,
                        "quantity": 10.0,
                    },
                ],
                "asks": [
                    {
                        "price": 1.01,
                        "quantity": 10.0,
                    },
                ],
                "paper_only": True,
                "live_order_submitted": False,
            }

    registry = NativeFallbackExchangeRegistry()

    registry.register(
        "weex",
        lambda exchange: (
            WeexNativeOrderBookProvider(
                provider=FakeWeexBackend()
            )
        ),
    )

    provider = (
        VerifiedNativeOrderBookProviderFactory(
            registry=registry
        )
        .build(
            WeexExchange()
        )
    )

    assert isinstance(
        provider,
        WeexNativeOrderBookProvider,
    )


def test_default_factory_builds_weex_provider():
    from exchanges.weex_native_order_book_provider import (
        WeexNativeOrderBookProvider,
    )

    class WeexExchange:
        id = "weex"

    provider = (
        VerifiedNativeOrderBookProviderFactory()
        .build(
            WeexExchange()
        )
    )

    assert isinstance(
        provider,
        WeexNativeOrderBookProvider,
    )
