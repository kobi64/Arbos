from core.native_coverage_exchange_set_registry import (
    NativeCoverageExchangeSetRegistry,
)


class FakeExchange:
    def __init__(self, config=None):
        self.config = config or {}


class FakeCCXT:
    gate = FakeExchange
    bitget = FakeExchange
    htx = FakeExchange
    xt = FakeExchange
    kucoin = FakeExchange
    digifinex = FakeExchange


def test_registers_default_native_coverage_exchange_set():
    registry = NativeCoverageExchangeSetRegistry(
        ccxt_module=FakeCCXT,
    )

    assert registry.enabled_exchange_ids() == [
        "bitget",
        "digifinex",
        "gate",
        "htx",
        "kucoin",
        "xt",
    ]


def test_builds_exchange_map_for_enabled_set():
    registry = NativeCoverageExchangeSetRegistry(
        ccxt_module=FakeCCXT,
    )

    exchanges = registry.build_exchange_map()

    assert sorted(exchanges) == [
        "bitget",
        "digifinex",
        "gate",
        "htx",
        "kucoin",
        "xt",
    ]

    assert isinstance(
        exchanges["gate"],
        FakeExchange,
    )

    assert exchanges["gate"].config[
        "enableRateLimit"
    ] is True


def test_can_disable_exchange():
    registry = NativeCoverageExchangeSetRegistry(
        ccxt_module=FakeCCXT,
    )

    registry.set_enabled(
        "xt",
        False,
    )

    assert "xt" not in (
        registry.enabled_exchange_ids()
    )

    exchanges = registry.build_exchange_map()

    assert "xt" not in exchanges


def test_can_start_with_custom_exchange_set():
    registry = NativeCoverageExchangeSetRegistry(
        ccxt_module=FakeCCXT,
        exchange_ids=[
            "gate",
            "kucoin",
        ],
    )

    assert registry.enabled_exchange_ids() == [
        "gate",
        "kucoin",
    ]

    assert sorted(
        registry.build_exchange_map()
    ) == [
        "gate",
        "kucoin",
    ]


def test_unknown_ccxt_exchange_is_rejected():
    try:
        NativeCoverageExchangeSetRegistry(
            ccxt_module=FakeCCXT,
            exchange_ids=[
                "gate",
                "unknown",
            ],
        )
        assert False
    except ValueError as exc:
        assert str(exc) == (
            "ccxt exchange not available"
        )


def test_public_exchange_instances_have_no_credentials():
    registry = NativeCoverageExchangeSetRegistry(
        ccxt_module=FakeCCXT,
        exchange_ids=[
            "gate",
        ],
    )

    exchange = (
        registry.build_exchange_map()[
            "gate"
        ]
    )

    assert "apiKey" not in exchange.config
    assert "secret" not in exchange.config


def test_requires_ccxt_module():
    try:
        NativeCoverageExchangeSetRegistry(
            ccxt_module=None,
        )
        assert False
    except ValueError as exc:
        assert str(exc) == (
            "ccxt_module is required"
        )


def test_registry_is_configuration_only():
    registry = NativeCoverageExchangeSetRegistry(
        ccxt_module=FakeCCXT,
        exchange_ids=[],
    )

    result = registry.build_exchange_map()

    assert result == {}
    assert registry.live_order_submitted is False
