from exchanges.native_coverage_entry_factory import (
    NativeCoverageEntryFactory,
)
from exchanges.bitget_native_market_source import (
    BitgetNativeMarketSource,
)
from exchanges.digifinex_native_market_source import (
    DigiFinexNativeMarketSource,
)
from exchanges.gate_native_market_source import (
    GateNativeMarketSource,
)
from exchanges.htx_native_market_source import (
    HTXNativeMarketSource,
)
from exchanges.kucoin_native_market_source import (
    KuCoinNativeMarketSource,
)
from exchanges.xt_native_market_source import (
    XTNativeMarketSource,
)


class FakeExchange:
    def __init__(self, exchange_id):
        self.id = exchange_id


def test_builds_entries_for_supported_exchanges():
    exchanges = {
        "gate": FakeExchange("gate"),
        "bitget": FakeExchange("bitget"),
        "htx": FakeExchange("htx"),
        "xt": FakeExchange("xt"),
        "kucoin": FakeExchange("kucoin"),
        "digifinex": FakeExchange("digifinex"),
    }

    result = NativeCoverageEntryFactory().build(
        exchanges
    )

    assert result["entry_count"] == 6

    entries = {
        item["exchange"].id: item
        for item in result["entries"]
    }

    assert isinstance(
        entries["gate"]["native_market_source"],
        GateNativeMarketSource,
    )
    assert isinstance(
        entries["bitget"]["native_market_source"],
        BitgetNativeMarketSource,
    )
    assert isinstance(
        entries["htx"]["native_market_source"],
        HTXNativeMarketSource,
    )
    assert isinstance(
        entries["xt"]["native_market_source"],
        XTNativeMarketSource,
    )
    assert isinstance(
        entries["kucoin"]["native_market_source"],
        KuCoinNativeMarketSource,
    )
    assert isinstance(
        entries["digifinex"]["native_market_source"],
        DigiFinexNativeMarketSource,
    )


def test_unknown_exchange_is_skipped_and_reported():
    exchanges = {
        "gate": FakeExchange("gate"),
        "unknown": FakeExchange("unknown"),
    }

    result = NativeCoverageEntryFactory().build(
        exchanges
    )

    assert result["entry_count"] == 1
    assert result["unsupported_exchange_count"] == 1

    assert result["unsupported_exchange_ids"] == [
        "unknown",
    ]


def test_none_exchange_value_is_skipped():
    result = NativeCoverageEntryFactory().build({
        "gate": None,
    })

    assert result["entry_count"] == 0
    assert result["invalid_exchange_count"] == 1


def test_exchange_id_comes_from_exchange_object():
    result = NativeCoverageEntryFactory().build({
        "wrong-key": FakeExchange("kucoin"),
    })

    assert result["entry_count"] == 1

    entry = result["entries"][0]

    assert entry["exchange"].id == "kucoin"
    assert isinstance(
        entry["native_market_source"],
        KuCoinNativeMarketSource,
    )


def test_requires_exchange_map():
    try:
        NativeCoverageEntryFactory().build(None)
        assert False
    except ValueError as exc:
        assert str(exc) == "exchanges are required"


def test_factory_is_configuration_only():
    result = NativeCoverageEntryFactory().build({})

    assert result["build_complete"] is True
    assert result["live_order_submitted"] is False


class FakeOrderBookProvider:
    def __init__(self, exchange):
        self.exchange = exchange


def test_configures_order_book_provider_for_exchange():
    digifinex = FakeExchange("digifinex")

    factory = NativeCoverageEntryFactory(
        provider_factories={
            "digifinex": FakeOrderBookProvider,
        },
        depth_sample_sizes={
            "digifinex": 20,
        },
    )

    result = factory.build({
        "digifinex": digifinex,
    })

    entry = result["entries"][0]

    assert isinstance(
        entry["order_book_provider"],
        FakeOrderBookProvider,
    )

    assert (
        entry["order_book_provider"].exchange
        is digifinex
    )

    assert entry["depth_sample_size"] == 20


def test_exchange_without_provider_has_no_depth_configuration():
    factory = NativeCoverageEntryFactory(
        provider_factories={
            "digifinex": FakeOrderBookProvider,
        },
        depth_sample_sizes={
            "digifinex": 20,
        },
    )

    result = factory.build({
        "gate": FakeExchange("gate"),
    })

    entry = result["entries"][0]

    assert "order_book_provider" not in entry
    assert "depth_sample_size" not in entry


def test_default_depth_sample_size_used_when_not_configured():
    factory = NativeCoverageEntryFactory(
        provider_factories={
            "digifinex": FakeOrderBookProvider,
        },
        default_depth_sample_size=10,
    )

    result = factory.build({
        "digifinex": FakeExchange(
            "digifinex"
        ),
    })

    assert result["entries"][0][
        "depth_sample_size"
    ] == 10


def test_invalid_depth_sample_size_is_rejected():
    try:
        NativeCoverageEntryFactory(
            provider_factories={
                "digifinex": FakeOrderBookProvider,
            },
            default_depth_sample_size=0,
        )
        assert False
    except ValueError as exc:
        assert str(exc) == (
            "default_depth_sample_size "
            "must be positive"
        )


def test_builds_hotcoin_native_market_entry():
    from exchanges.hotcoin_native_market_source import (
        HotcoinNativeMarketSource,
    )

    hotcoin = FakeExchange(
        "hotcoin"
    )

    result = (
        NativeCoverageEntryFactory()
        .build({
            "hotcoin": hotcoin,
        })
    )

    assert result[
        "entry_count"
    ] == 1

    entry = result[
        "entries"
    ][0]

    assert entry[
        "exchange"
    ] is hotcoin

    assert isinstance(
        entry[
            "native_market_source"
        ],
        HotcoinNativeMarketSource,
    )


def test_hotcoin_has_no_depth_provider_by_default():
    result = (
        NativeCoverageEntryFactory()
        .build({
            "hotcoin": FakeExchange(
                "hotcoin"
            ),
        })
    )

    entry = result[
        "entries"
    ][0]

    assert (
        "order_book_provider"
        not in entry
    )

    assert (
        "depth_sample_size"
        not in entry
    )


def test_builds_coinex_native_market_source():
    from exchanges.coinex_native_market_source import (
        CoinExNativeMarketSource,
    )

    result = NativeCoverageEntryFactory().build({
        "coinex": FakeExchange("coinex"),
    })

    assert result["entry_count"] == 1

    entry = result["entries"][0]

    assert isinstance(
        entry["native_market_source"],
        CoinExNativeMarketSource,
    )


def test_coinex_exchange_id_is_normalized():
    from exchanges.coinex_native_market_source import (
        CoinExNativeMarketSource,
    )

    result = NativeCoverageEntryFactory().build({
        "wrong-key": FakeExchange(" COINEX "),
    })

    assert result["entry_count"] == 1

    assert isinstance(
        result["entries"][0][
            "native_market_source"
        ],
        CoinExNativeMarketSource,
    )


def test_builds_phemex_native_market_source():
    from exchanges.phemex_native_market_source import (
        PhemexNativeMarketSource,
    )

    result = NativeCoverageEntryFactory().build({
        "phemex": FakeExchange("phemex"),
    })

    assert result["entry_count"] == 1

    entry = result["entries"][0]

    assert isinstance(
        entry["native_market_source"],
        PhemexNativeMarketSource,
    )


def test_phemex_exchange_id_is_normalized():
    from exchanges.phemex_native_market_source import (
        PhemexNativeMarketSource,
    )

    result = NativeCoverageEntryFactory().build({
        "wrong-key": FakeExchange(" PHEMEX "),
    })

    assert result["entry_count"] == 1

    assert isinstance(
        result["entries"][0][
            "native_market_source"
        ],
        PhemexNativeMarketSource,
    )


def test_builds_okx_native_market_source():
    from exchanges.okx_native_market_source import (
        OKXNativeMarketSource,
    )

    result = NativeCoverageEntryFactory().build({
        "okx": FakeExchange("okx"),
    })

    assert result["entry_count"] == 1

    entry = result["entries"][0]

    assert isinstance(
        entry["native_market_source"],
        OKXNativeMarketSource,
    )


def test_okx_exchange_id_is_normalized():
    from exchanges.okx_native_market_source import (
        OKXNativeMarketSource,
    )

    result = NativeCoverageEntryFactory().build({
        "wrong-key": FakeExchange(" OKX "),
    })

    assert result["entry_count"] == 1

    assert isinstance(
        result["entries"][0][
            "native_market_source"
        ],
        OKXNativeMarketSource,
    )
