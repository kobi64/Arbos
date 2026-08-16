from core.native_coverage_exchange_set_registry import (
    NativeCoverageExchangeSetRegistry,
)


class FakeExchange:
    def __init__(self, config=None):
        self.config = config or {}


class FakeCCXT:
    binance = FakeExchange
    bingx = FakeExchange
    bitget = FakeExchange
    bitrue = FakeExchange
    coinbase = FakeExchange
    coinex = FakeExchange
    digifinex = FakeExchange
    gate = FakeExchange
    htx = FakeExchange
    kraken = FakeExchange
    kucoin = FakeExchange
    lbank = FakeExchange
    mexc = FakeExchange
    okx = FakeExchange
    ourbit = FakeExchange
    phemex = FakeExchange
    poloniex = FakeExchange
    toobit = FakeExchange
    weex = FakeExchange
    whitebit = FakeExchange
    xt = FakeExchange


def test_registers_default_native_coverage_exchange_set():
    registry = NativeCoverageExchangeSetRegistry(
        ccxt_module=FakeCCXT,
    )

    assert registry.enabled_exchange_ids() == [
        "binance",
        "bingx",
        "bitget",
        "bitrue",
        "coinbase",
        "coinex",
        "digifinex",
        "gate",
        "htx",
        "kraken",
        "kucoin",
        "lbank",
        "mexc",
        "okx",
        "ourbit",
        "phemex",
        "poloniex",
        "toobit",
        "weex",
        "whitebit",
        "xt",
    ]


def test_builds_exchange_map_for_enabled_set():
    registry = NativeCoverageExchangeSetRegistry(
        ccxt_module=FakeCCXT,
    )

    exchanges = registry.build_exchange_map()

    assert sorted(exchanges) == [
        "binance",
        "bingx",
        "bitget",
        "bitrue",
        "coinbase",
        "coinex",
        "digifinex",
        "gate",
        "htx",
        "kraken",
        "kucoin",
        "lbank",
        "mexc",
        "okx",
        "ourbit",
        "phemex",
        "poloniex",
        "toobit",
        "weex",
        "whitebit",
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


def test_default_set_includes_all_verified_native_coverage_venues():
    expected = {
        "binance",
        "bingx",
        "bitget",
        "bitrue",
        "coinbase",
        "coinex",
        "digifinex",
        "gate",
        "htx",
        "kraken",
        "kucoin",
        "lbank",
        "mexc",
        "okx",
        "ourbit",
        "phemex",
        "poloniex",
        "toobit",
        "weex",
        "whitebit",
        "xt",
    }

    assert set(
        NativeCoverageExchangeSetRegistry
        .DEFAULT_EXCHANGE_IDS
    ) == expected


def test_default_set_excludes_unverified_hotcoin():
    assert (
        "hotcoin"
        not in
        NativeCoverageExchangeSetRegistry
        .DEFAULT_EXCHANGE_IDS
    )


def test_default_set_has_no_duplicate_exchange_ids():
    exchange_ids = (
        NativeCoverageExchangeSetRegistry
        .DEFAULT_EXCHANGE_IDS
    )

    assert len(exchange_ids) == len(
        set(exchange_ids)
    )


def test_default_set_can_include_verified_native_only_exchange():
    class CCXTWithoutOurbit:
        binance = FakeExchange
        bingx = FakeExchange
        bitget = FakeExchange
        bitrue = FakeExchange
        coinbase = FakeExchange
        coinex = FakeExchange
        digifinex = FakeExchange
        gate = FakeExchange
        htx = FakeExchange
        kraken = FakeExchange
        kucoin = FakeExchange
        lbank = FakeExchange
        mexc = FakeExchange
        okx = FakeExchange
        phemex = FakeExchange
        poloniex = FakeExchange
        toobit = FakeExchange
        weex = FakeExchange
        whitebit = FakeExchange
        xt = FakeExchange

    registry = NativeCoverageExchangeSetRegistry(
        ccxt_module=CCXTWithoutOurbit,
    )

    assert "ourbit" in (
        registry.enabled_exchange_ids()
    )

    exchanges = registry.build_exchange_map()

    assert "ourbit" in exchanges
    assert exchanges["ourbit"].id == "ourbit"
