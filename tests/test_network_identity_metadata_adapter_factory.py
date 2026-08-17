from exchanges.ccxt_network_identity_metadata_adapter import (
    CCXTNetworkIdentityMetadataAdapter,
)
from exchanges.network_identity_metadata_adapter_factory import (
    NetworkIdentityMetadataAdapterFactory,
)
from exchanges.poloniex_network_identity_metadata_adapter import (
    PoloniexNetworkIdentityMetadataAdapter,
)


class FakeExchange:
    def __init__(self, exchange_id):
        self.id = exchange_id
        self.currencies = {}

    def load_currencies(self):
        return {}

    def load_markets(self):
        self.currencies = {}
        return {}


class FakePoloniexProvider:
    pass


def test_poloniex_builds_native_identity_adapter():
    factory = NetworkIdentityMetadataAdapterFactory(
        poloniex_provider_factory=(
            lambda exchange: FakePoloniexProvider()
        )
    )

    adapter = factory.build(
        FakeExchange("poloniex")
    )

    assert isinstance(
        adapter,
        PoloniexNetworkIdentityMetadataAdapter,
    )


def test_unknown_exchange_uses_ccxt_identity_adapter():
    factory = NetworkIdentityMetadataAdapterFactory()

    adapter = factory.build(
        FakeExchange("unknown")
    )

    assert isinstance(
        adapter,
        CCXTNetworkIdentityMetadataAdapter,
    )


def test_exchange_id_is_normalized():
    factory = NetworkIdentityMetadataAdapterFactory(
        poloniex_provider_factory=(
            lambda exchange: FakePoloniexProvider()
        )
    )

    adapter = factory.build(
        FakeExchange(" POLONIEX ")
    )

    assert isinstance(
        adapter,
        PoloniexNetworkIdentityMetadataAdapter,
    )


def test_missing_exchange_is_rejected():
    factory = NetworkIdentityMetadataAdapterFactory()

    try:
        factory.build(None)
        assert False
    except ValueError as exc:
        assert str(exc) == "exchange is required"


def test_custom_poloniex_provider_factory_is_used():
    marker = object()
    calls = []

    def provider_factory(exchange):
        calls.append(exchange)
        return marker

    factory = NetworkIdentityMetadataAdapterFactory(
        poloniex_provider_factory=(
            provider_factory
        )
    )

    exchange = FakeExchange(
        "poloniex"
    )

    adapter = factory.build(
        exchange
    )

    assert calls == [
        exchange
    ]

    assert adapter._provider is marker


def test_mexc_builds_native_identity_adapter():
    from exchanges.mexc_network_identity_metadata_adapter import (
        MexcNetworkIdentityMetadataAdapter,
    )

    class MexcExchange:
        id = "mexc"

    marker = object()

    factory = NetworkIdentityMetadataAdapterFactory(
        mexc_provider_factory=(
            lambda exchange: marker
        ),
    )

    adapter = factory.build(
        MexcExchange()
    )

    assert isinstance(
        adapter,
        MexcNetworkIdentityMetadataAdapter,
    )

    assert adapter._provider is marker


def test_mexc_exchange_id_is_normalized():
    from exchanges.mexc_network_identity_metadata_adapter import (
        MexcNetworkIdentityMetadataAdapter,
    )

    class MexcExchange:
        id = " MEXC "

    marker = object()

    factory = NetworkIdentityMetadataAdapterFactory(
        mexc_provider_factory=(
            lambda exchange: marker
        ),
    )

    adapter = factory.build(
        MexcExchange()
    )

    assert isinstance(
        adapter,
        MexcNetworkIdentityMetadataAdapter,
    )


def test_default_factory_builds_mexc_identity_adapter():
    from exchanges.mexc_network_identity_metadata_adapter import (
        MexcNetworkIdentityMetadataAdapter,
    )

    class MexcExchange:
        id = "mexc"

    adapter = (
        NetworkIdentityMetadataAdapterFactory()
        .build(
            MexcExchange()
        )
    )

    assert isinstance(
        adapter,
        MexcNetworkIdentityMetadataAdapter,
    )


def test_lbank_builds_native_identity_adapter():
    from exchanges.lbank_network_identity_metadata_adapter import (
        LBankNetworkIdentityMetadataAdapter,
    )

    class LBankExchange:
        id = "lbank"

    marker = object()

    factory = NetworkIdentityMetadataAdapterFactory(
        lbank_provider_factory=(
            lambda exchange: marker
        ),
    )

    adapter = factory.build(
        LBankExchange()
    )

    assert isinstance(
        adapter,
        LBankNetworkIdentityMetadataAdapter,
    )

    assert adapter._provider is marker


def test_lbank_exchange_id_is_normalized():
    from exchanges.lbank_network_identity_metadata_adapter import (
        LBankNetworkIdentityMetadataAdapter,
    )

    class LBankExchange:
        id = " LBANK "

    marker = object()

    factory = NetworkIdentityMetadataAdapterFactory(
        lbank_provider_factory=(
            lambda exchange: marker
        ),
    )

    adapter = factory.build(
        LBankExchange()
    )

    assert isinstance(
        adapter,
        LBankNetworkIdentityMetadataAdapter,
    )


def test_default_factory_builds_lbank_identity_adapter():
    from exchanges.lbank_network_identity_metadata_adapter import (
        LBankNetworkIdentityMetadataAdapter,
    )

    class LBankExchange:
        id = "lbank"

    adapter = (
        NetworkIdentityMetadataAdapterFactory()
        .build(
            LBankExchange()
        )
    )

    assert isinstance(
        adapter,
        LBankNetworkIdentityMetadataAdapter,
    )


def test_ourbit_native_only_exchange_fails_closed_for_identity():
    class OurbitExchange:
        id = "ourbit"

    adapter = (
        NetworkIdentityMetadataAdapterFactory()
        .build(
            OurbitExchange()
        )
    )

    records = adapter.get_records(
        "USDT"
    )

    assert records == []


def test_gate_builds_native_identity_adapter():
    from exchanges.gateio_network_identity_metadata_adapter import (
        GateIONetworkIdentityMetadataAdapter,
    )

    marker = object()

    factory = NetworkIdentityMetadataAdapterFactory(
        gateio_client_factory=(
            lambda exchange: marker
        ),
    )

    adapter = factory.build(
        FakeExchange("gate")
    )

    assert isinstance(
        adapter,
        GateIONetworkIdentityMetadataAdapter,
    )
    assert adapter._client is marker


def test_gateio_exchange_id_is_supported():
    from exchanges.gateio_network_identity_metadata_adapter import (
        GateIONetworkIdentityMetadataAdapter,
    )

    marker = object()

    factory = NetworkIdentityMetadataAdapterFactory(
        gateio_client_factory=(
            lambda exchange: marker
        ),
    )

    adapter = factory.build(
        FakeExchange(" GATEIO ")
    )

    assert isinstance(
        adapter,
        GateIONetworkIdentityMetadataAdapter,
    )


def test_kucoin_builds_native_identity_adapter():
    from exchanges.kucoin_network_identity_metadata_adapter import (
        KuCoinNetworkIdentityMetadataAdapter,
    )

    marker = object()

    factory = NetworkIdentityMetadataAdapterFactory(
        kucoin_client_factory=(
            lambda exchange: marker
        ),
    )

    adapter = factory.build(
        FakeExchange("kucoin")
    )

    assert isinstance(
        adapter,
        KuCoinNetworkIdentityMetadataAdapter,
    )
    assert adapter._client is marker


def test_kucoin_exchange_id_is_normalized():
    from exchanges.kucoin_network_identity_metadata_adapter import (
        KuCoinNetworkIdentityMetadataAdapter,
    )

    marker = object()

    factory = NetworkIdentityMetadataAdapterFactory(
        kucoin_client_factory=(
            lambda exchange: marker
        ),
    )

    adapter = factory.build(
        FakeExchange(" KUCOIN ")
    )

    assert isinstance(
        adapter,
        KuCoinNetworkIdentityMetadataAdapter,
    )


def test_default_factory_builds_gate_identity_adapter():
    from exchanges.gateio_network_identity_metadata_adapter import (
        GateIONetworkIdentityMetadataAdapter,
    )

    adapter = (
        NetworkIdentityMetadataAdapterFactory()
        .build(
            FakeExchange("gate")
        )
    )

    assert isinstance(
        adapter,
        GateIONetworkIdentityMetadataAdapter,
    )


def test_default_factory_builds_kucoin_identity_adapter():
    from exchanges.kucoin_network_identity_metadata_adapter import (
        KuCoinNetworkIdentityMetadataAdapter,
    )

    adapter = (
        NetworkIdentityMetadataAdapterFactory()
        .build(
            FakeExchange("kucoin")
        )
    )

    assert isinstance(
        adapter,
        KuCoinNetworkIdentityMetadataAdapter,
    )
