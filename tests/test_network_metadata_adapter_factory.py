from exchanges.ccxt_network_metadata_adapter import (
    CCXTNetworkMetadataAdapter,
)
from exchanges.network_metadata_adapter_factory import (
    NetworkMetadataAdapterFactory,
)
from exchanges.weex_network_metadata_adapter import (
    WeexNetworkMetadataAdapter,
)


class FakeExchange:
    def __init__(self, exchange_id):
        self.id = exchange_id

    def load_currencies(self):
        return {}


class FakeWeexProvider:
    pass


def test_weex_builds_weex_network_adapter():
    factory = NetworkMetadataAdapterFactory(
        weex_provider_factory=(
            lambda exchange: FakeWeexProvider()
        )
    )

    adapter = factory.build(
        FakeExchange("weex")
    )

    assert isinstance(
        adapter,
        WeexNetworkMetadataAdapter,
    )


def test_non_weex_exchange_uses_ccxt_adapter():
    factory = NetworkMetadataAdapterFactory()

    adapter = factory.build(
        FakeExchange("kucoin")
    )

    assert isinstance(
        adapter,
        CCXTNetworkMetadataAdapter,
    )


def test_unknown_exchange_uses_ccxt_adapter():
    factory = NetworkMetadataAdapterFactory()

    adapter = factory.build(
        FakeExchange("unknown")
    )

    assert isinstance(
        adapter,
        CCXTNetworkMetadataAdapter,
    )


def test_exchange_id_is_normalized():
    factory = NetworkMetadataAdapterFactory(
        weex_provider_factory=(
            lambda exchange: FakeWeexProvider()
        )
    )

    adapter = factory.build(
        FakeExchange(" WEEX ")
    )

    assert isinstance(
        adapter,
        WeexNetworkMetadataAdapter,
    )


def test_missing_exchange_is_rejected():
    factory = NetworkMetadataAdapterFactory()

    try:
        factory.build(None)
        assert False
    except ValueError as exc:
        assert str(exc) == "exchange is required"


def test_custom_weex_provider_factory_is_used():
    marker = object()
    calls = []

    def provider_factory(exchange):
        calls.append(exchange)
        return marker

    factory = NetworkMetadataAdapterFactory(
        weex_provider_factory=(
            provider_factory
        )
    )

    exchange = FakeExchange("weex")

    adapter = factory.build(
        exchange
    )

    assert calls == [
        exchange
    ]

    assert adapter._provider is marker


def test_poloniex_builds_native_network_adapter():
    from exchanges.poloniex_network_metadata_adapter import (
        PoloniexNetworkMetadataAdapter,
    )

    class PoloniexExchange:
        id = "poloniex"

    marker = object()

    factory = NetworkMetadataAdapterFactory(
        poloniex_provider_factory=(
            lambda exchange: marker
        ),
    )

    adapter = factory.build(
        PoloniexExchange()
    )

    assert isinstance(
        adapter,
        PoloniexNetworkMetadataAdapter,
    )

    assert adapter._provider is marker


def test_poloniex_exchange_id_is_normalized():
    from exchanges.poloniex_network_metadata_adapter import (
        PoloniexNetworkMetadataAdapter,
    )

    class PoloniexExchange:
        id = " POLONIEX "

    marker = object()

    factory = NetworkMetadataAdapterFactory(
        poloniex_provider_factory=(
            lambda exchange: marker
        ),
    )

    adapter = factory.build(
        PoloniexExchange()
    )

    assert isinstance(
        adapter,
        PoloniexNetworkMetadataAdapter,
    )


def test_default_factory_builds_poloniex_network_adapter():
    from exchanges.poloniex_network_metadata_adapter import (
        PoloniexNetworkMetadataAdapter,
    )

    class PoloniexExchange:
        id = "poloniex"

    adapter = (
        NetworkMetadataAdapterFactory()
        .build(
            PoloniexExchange()
        )
    )

    assert isinstance(
        adapter,
        PoloniexNetworkMetadataAdapter,
    )


def test_mexc_builds_native_network_adapter():
    from exchanges.mexc_network_metadata_adapter import (
        MexcNetworkMetadataAdapter,
    )

    class MexcExchange:
        id = "mexc"

    marker = object()

    factory = NetworkMetadataAdapterFactory(
        mexc_provider_factory=(
            lambda exchange: marker
        ),
    )

    adapter = factory.build(
        MexcExchange()
    )

    assert isinstance(
        adapter,
        MexcNetworkMetadataAdapter,
    )

    assert adapter._provider is marker


def test_mexc_exchange_id_is_normalized():
    from exchanges.mexc_network_metadata_adapter import (
        MexcNetworkMetadataAdapter,
    )

    class MexcExchange:
        id = " MEXC "

    marker = object()

    factory = NetworkMetadataAdapterFactory(
        mexc_provider_factory=(
            lambda exchange: marker
        ),
    )

    adapter = factory.build(
        MexcExchange()
    )

    assert isinstance(
        adapter,
        MexcNetworkMetadataAdapter,
    )


def test_default_factory_builds_mexc_network_adapter():
    from exchanges.mexc_network_metadata_adapter import (
        MexcNetworkMetadataAdapter,
    )

    class MexcExchange:
        id = "mexc"

    adapter = (
        NetworkMetadataAdapterFactory()
        .build(
            MexcExchange()
        )
    )

    assert isinstance(
        adapter,
        MexcNetworkMetadataAdapter,
    )


def test_ourbit_builds_native_network_adapter():
    from exchanges.ourbit_network_metadata_adapter import (
        OurbitNetworkMetadataAdapter,
    )

    class OurbitExchange:
        id = "ourbit"

    marker = object()

    factory = NetworkMetadataAdapterFactory(
        ourbit_client_factory=(
            lambda exchange: marker
        ),
    )

    adapter = factory.build(
        OurbitExchange()
    )

    assert isinstance(
        adapter,
        OurbitNetworkMetadataAdapter,
    )

    assert adapter._client is marker


def test_ourbit_exchange_id_is_normalized():
    from exchanges.ourbit_network_metadata_adapter import (
        OurbitNetworkMetadataAdapter,
    )

    class OurbitExchange:
        id = " OURBIT "

    marker = object()

    factory = NetworkMetadataAdapterFactory(
        ourbit_client_factory=(
            lambda exchange: marker
        ),
    )

    adapter = factory.build(
        OurbitExchange()
    )

    assert isinstance(
        adapter,
        OurbitNetworkMetadataAdapter,
    )


def test_default_factory_builds_ourbit_network_adapter():
    from exchanges.ourbit_network_metadata_adapter import (
        OurbitNetworkMetadataAdapter,
    )

    class OurbitExchange:
        id = "ourbit"

    adapter = (
        NetworkMetadataAdapterFactory()
        .build(
            OurbitExchange()
        )
    )

    assert isinstance(
        adapter,
        OurbitNetworkMetadataAdapter,
    )


def test_lbank_builds_native_network_adapter():
    from exchanges.lbank_network_metadata_adapter import (
        LBankNetworkMetadataAdapter,
    )

    class LBankExchange:
        id = "lbank"

    marker = object()

    factory = NetworkMetadataAdapterFactory(
        lbank_provider_factory=(
            lambda exchange: marker
        ),
    )

    adapter = factory.build(
        LBankExchange()
    )

    assert isinstance(
        adapter,
        LBankNetworkMetadataAdapter,
    )

    assert adapter._provider is marker


def test_lbank_exchange_id_is_normalized():
    from exchanges.lbank_network_metadata_adapter import (
        LBankNetworkMetadataAdapter,
    )

    class LBankExchange:
        id = " LBANK "

    marker = object()

    factory = NetworkMetadataAdapterFactory(
        lbank_provider_factory=(
            lambda exchange: marker
        ),
    )

    adapter = factory.build(
        LBankExchange()
    )

    assert isinstance(
        adapter,
        LBankNetworkMetadataAdapter,
    )


def test_default_factory_builds_lbank_network_adapter():
    from exchanges.lbank_network_metadata_adapter import (
        LBankNetworkMetadataAdapter,
    )

    class LBankExchange:
        id = "lbank"

    adapter = (
        NetworkMetadataAdapterFactory()
        .build(
            LBankExchange()
        )
    )

    assert isinstance(
        adapter,
        LBankNetworkMetadataAdapter,
    )


def test_bingx_builds_native_network_adapter():
    from exchanges.bingx_network_metadata_adapter import (
        BingXNetworkMetadataAdapter,
    )

    class BingXExchange:
        id = "bingx"

    marker = object()

    factory = NetworkMetadataAdapterFactory(
        bingx_client_factory=(
            lambda exchange: marker
        ),
    )

    adapter = factory.build(
        BingXExchange()
    )

    assert isinstance(
        adapter,
        BingXNetworkMetadataAdapter,
    )

    assert adapter._client is marker


def test_bingx_exchange_id_is_normalized():
    from exchanges.bingx_network_metadata_adapter import (
        BingXNetworkMetadataAdapter,
    )

    class BingXExchange:
        id = " BINGX "

    marker = object()

    factory = NetworkMetadataAdapterFactory(
        bingx_client_factory=(
            lambda exchange: marker
        ),
    )

    adapter = factory.build(
        BingXExchange()
    )

    assert isinstance(
        adapter,
        BingXNetworkMetadataAdapter,
    )


def test_default_factory_builds_bingx_network_adapter():
    from exchanges.bingx_network_metadata_adapter import (
        BingXNetworkMetadataAdapter,
    )

    class BingXExchange:
        id = "bingx"

    adapter = (
        NetworkMetadataAdapterFactory()
        .build(
            BingXExchange()
        )
    )

    assert isinstance(
        adapter,
        BingXNetworkMetadataAdapter,
    )


def test_kraken_builds_native_network_adapter():
    from exchanges.kraken_network_metadata_adapter import (
        KrakenNetworkMetadataAdapter,
    )

    class KrakenExchange:
        id = "kraken"

    marker = object()

    factory = NetworkMetadataAdapterFactory(
        kraken_client_factory=(
            lambda exchange: marker
        ),
    )

    adapter = factory.build(
        KrakenExchange()
    )

    assert isinstance(
        adapter,
        KrakenNetworkMetadataAdapter,
    )

    assert adapter._client is marker


def test_kraken_exchange_id_is_normalized():
    from exchanges.kraken_network_metadata_adapter import (
        KrakenNetworkMetadataAdapter,
    )

    class KrakenExchange:
        id = " KRAKEN "

    marker = object()

    factory = NetworkMetadataAdapterFactory(
        kraken_client_factory=(
            lambda exchange: marker
        ),
    )

    adapter = factory.build(
        KrakenExchange()
    )

    assert isinstance(
        adapter,
        KrakenNetworkMetadataAdapter,
    )


def test_default_factory_builds_kraken_network_adapter():
    from exchanges.kraken_network_metadata_adapter import (
        KrakenNetworkMetadataAdapter,
    )

    class KrakenExchange:
        id = "kraken"

    adapter = (
        NetworkMetadataAdapterFactory()
        .build(
            KrakenExchange()
        )
    )

    assert isinstance(
        adapter,
        KrakenNetworkMetadataAdapter,
    )


def test_gateio_builds_native_network_adapter():
    from exchanges.gateio_network_metadata_adapter import (
        GateIONetworkMetadataAdapter,
    )

    class GateIOExchange:
        id = "gateio"

    marker = object()

    factory = NetworkMetadataAdapterFactory(
        gateio_client_factory=(
            lambda exchange: marker
        ),
    )

    adapter = factory.build(
        GateIOExchange()
    )

    assert isinstance(
        adapter,
        GateIONetworkMetadataAdapter,
    )

    assert adapter._client is marker


def test_gateio_exchange_id_is_normalized():
    from exchanges.gateio_network_metadata_adapter import (
        GateIONetworkMetadataAdapter,
    )

    class GateIOExchange:
        id = " GATEIO "

    marker = object()

    factory = NetworkMetadataAdapterFactory(
        gateio_client_factory=(
            lambda exchange: marker
        ),
    )

    adapter = factory.build(
        GateIOExchange()
    )

    assert isinstance(
        adapter,
        GateIONetworkMetadataAdapter,
    )


def test_default_factory_builds_gateio_network_adapter():
    from exchanges.gateio_network_metadata_adapter import (
        GateIONetworkMetadataAdapter,
    )

    class GateIOExchange:
        id = "gateio"

    adapter = (
        NetworkMetadataAdapterFactory()
        .build(
            GateIOExchange()
        )
    )

    assert isinstance(
        adapter,
        GateIONetworkMetadataAdapter,
    )
