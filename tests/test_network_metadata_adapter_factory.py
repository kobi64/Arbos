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


def test_unregistered_exchange_uses_ccxt_adapter():
    factory = NetworkMetadataAdapterFactory()

    adapter = factory.build(
        FakeExchange("unregistered_exchange")
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


def test_kucoin_builds_native_network_adapter():
    from exchanges.kucoin_network_metadata_adapter import (
        KuCoinNetworkMetadataAdapter,
    )

    class KuCoinExchange:
        id = "kucoin"

    marker = object()

    factory = NetworkMetadataAdapterFactory(
        kucoin_client_factory=(
            lambda exchange: marker
        ),
    )

    adapter = factory.build(
        KuCoinExchange()
    )

    assert isinstance(
        adapter,
        KuCoinNetworkMetadataAdapter,
    )

    assert adapter._client is marker


def test_kucoin_exchange_id_is_normalized():
    from exchanges.kucoin_network_metadata_adapter import (
        KuCoinNetworkMetadataAdapter,
    )

    class KuCoinExchange:
        id = " KUCOIN "

    marker = object()

    factory = NetworkMetadataAdapterFactory(
        kucoin_client_factory=(
            lambda exchange: marker
        ),
    )

    adapter = factory.build(
        KuCoinExchange()
    )

    assert isinstance(
        adapter,
        KuCoinNetworkMetadataAdapter,
    )


def test_default_factory_builds_kucoin_network_adapter():
    from exchanges.kucoin_network_metadata_adapter import (
        KuCoinNetworkMetadataAdapter,
    )

    class KuCoinExchange:
        id = "kucoin"

    adapter = (
        NetworkMetadataAdapterFactory()
        .build(
            KuCoinExchange()
        )
    )

    assert isinstance(
        adapter,
        KuCoinNetworkMetadataAdapter,
    )


def test_htx_builds_native_network_adapter():
    from exchanges.htx_network_metadata_adapter import (
        HTXNetworkMetadataAdapter,
    )

    class HTXExchange:
        id = "htx"

    marker = object()

    factory = NetworkMetadataAdapterFactory(
        htx_client_factory=(
            lambda exchange: marker
        ),
    )

    adapter = factory.build(
        HTXExchange()
    )

    assert isinstance(
        adapter,
        HTXNetworkMetadataAdapter,
    )

    assert adapter._client is marker


def test_htx_exchange_id_is_normalized():
    from exchanges.htx_network_metadata_adapter import (
        HTXNetworkMetadataAdapter,
    )

    class HTXExchange:
        id = " HTX "

    marker = object()

    factory = NetworkMetadataAdapterFactory(
        htx_client_factory=(
            lambda exchange: marker
        ),
    )

    adapter = factory.build(
        HTXExchange()
    )

    assert isinstance(
        adapter,
        HTXNetworkMetadataAdapter,
    )


def test_default_factory_builds_htx_network_adapter():
    from exchanges.htx_network_metadata_adapter import (
        HTXNetworkMetadataAdapter,
    )

    class HTXExchange:
        id = "htx"

    adapter = (
        NetworkMetadataAdapterFactory()
        .build(
            HTXExchange()
        )
    )

    assert isinstance(
        adapter,
        HTXNetworkMetadataAdapter,
    )


def test_htx_builds_native_network_adapter():
    from exchanges.htx_network_metadata_adapter import (
        HTXNetworkMetadataAdapter,
    )

    class HTXExchange:
        id = "htx"

    marker = object()

    factory = NetworkMetadataAdapterFactory(
        htx_client_factory=(
            lambda exchange: marker
        ),
    )

    adapter = factory.build(
        HTXExchange()
    )

    assert isinstance(
        adapter,
        HTXNetworkMetadataAdapter,
    )

    assert adapter._client is marker


def test_htx_exchange_id_is_normalized():
    from exchanges.htx_network_metadata_adapter import (
        HTXNetworkMetadataAdapter,
    )

    class HTXExchange:
        id = " HTX "

    marker = object()

    factory = NetworkMetadataAdapterFactory(
        htx_client_factory=(
            lambda exchange: marker
        ),
    )

    adapter = factory.build(
        HTXExchange()
    )

    assert isinstance(
        adapter,
        HTXNetworkMetadataAdapter,
    )


def test_default_factory_builds_htx_network_adapter():
    from exchanges.htx_network_metadata_adapter import (
        HTXNetworkMetadataAdapter,
    )

    class HTXExchange:
        id = "htx"

    adapter = (
        NetworkMetadataAdapterFactory()
        .build(
            HTXExchange()
        )
    )

    assert isinstance(
        adapter,
        HTXNetworkMetadataAdapter,
    )


def test_digifinex_builds_native_network_adapter():
    from exchanges.digifinex_network_metadata_adapter import (
        DigiFinexNetworkMetadataAdapter,
    )

    class DigiFinexExchange:
        id = "digifinex"

    marker = object()

    factory = NetworkMetadataAdapterFactory(
        digifinex_client_factory=(
            lambda exchange: marker
        ),
    )

    adapter = factory.build(
        DigiFinexExchange()
    )

    assert isinstance(
        adapter,
        DigiFinexNetworkMetadataAdapter,
    )

    assert adapter._client is marker


def test_digifinex_exchange_id_is_normalized():
    from exchanges.digifinex_network_metadata_adapter import (
        DigiFinexNetworkMetadataAdapter,
    )

    class DigiFinexExchange:
        id = " DIGIFINEX "

    marker = object()

    factory = NetworkMetadataAdapterFactory(
        digifinex_client_factory=(
            lambda exchange: marker
        ),
    )

    adapter = factory.build(
        DigiFinexExchange()
    )

    assert isinstance(
        adapter,
        DigiFinexNetworkMetadataAdapter,
    )


def test_default_factory_builds_digifinex_network_adapter():
    from exchanges.digifinex_network_metadata_adapter import (
        DigiFinexNetworkMetadataAdapter,
    )

    class DigiFinexExchange:
        id = "digifinex"

    adapter = (
        NetworkMetadataAdapterFactory()
        .build(
            DigiFinexExchange()
        )
    )

    assert isinstance(
        adapter,
        DigiFinexNetworkMetadataAdapter,
    )


def test_bitget_builds_native_network_adapter():
    from exchanges.bitget_network_metadata_adapter import (
        BitgetNetworkMetadataAdapter,
    )

    class BitgetExchange:
        id = "bitget"

    marker = object()

    factory = NetworkMetadataAdapterFactory(
        bitget_client_factory=(
            lambda exchange: marker
        ),
    )

    adapter = factory.build(
        BitgetExchange()
    )

    assert isinstance(
        adapter,
        BitgetNetworkMetadataAdapter,
    )

    assert adapter._client is marker


def test_bitget_exchange_id_is_normalized():
    from exchanges.bitget_network_metadata_adapter import (
        BitgetNetworkMetadataAdapter,
    )

    class BitgetExchange:
        id = " BITGET "

    marker = object()

    factory = NetworkMetadataAdapterFactory(
        bitget_client_factory=(
            lambda exchange: marker
        ),
    )

    adapter = factory.build(
        BitgetExchange()
    )

    assert isinstance(
        adapter,
        BitgetNetworkMetadataAdapter,
    )


def test_default_factory_builds_bitget_network_adapter():
    from exchanges.bitget_network_metadata_adapter import (
        BitgetNetworkMetadataAdapter,
    )

    class BitgetExchange:
        id = "bitget"

    adapter = (
        NetworkMetadataAdapterFactory()
        .build(
            BitgetExchange()
        )
    )

    assert isinstance(
        adapter,
        BitgetNetworkMetadataAdapter,
    )


def test_xt_builds_native_network_adapter():
    from exchanges.xt_network_metadata_adapter import (
        XTNetworkMetadataAdapter,
    )

    class XTExchange:
        id = "xt"

    marker = object()

    factory = NetworkMetadataAdapterFactory(
        xt_client_factory=(
            lambda exchange: marker
        ),
    )

    adapter = factory.build(
        XTExchange()
    )

    assert isinstance(
        adapter,
        XTNetworkMetadataAdapter,
    )

    assert adapter._client is marker


def test_xt_exchange_id_is_normalized():
    from exchanges.xt_network_metadata_adapter import (
        XTNetworkMetadataAdapter,
    )

    class XTExchange:
        id = " XT "

    marker = object()

    factory = NetworkMetadataAdapterFactory(
        xt_client_factory=(
            lambda exchange: marker
        ),
    )

    adapter = factory.build(
        XTExchange()
    )

    assert isinstance(
        adapter,
        XTNetworkMetadataAdapter,
    )


def test_default_factory_builds_xt_network_adapter():
    from exchanges.xt_network_metadata_adapter import (
        XTNetworkMetadataAdapter,
    )

    class XTExchange:
        id = "xt"

    adapter = (
        NetworkMetadataAdapterFactory()
        .build(
            XTExchange()
        )
    )

    assert isinstance(
        adapter,
        XTNetworkMetadataAdapter,
    )


def test_coinex_builds_native_network_adapter():
    from exchanges.coinex_network_metadata_adapter import (
        CoinExNetworkMetadataAdapter,
    )

    class CoinExExchange:
        id = "coinex"

    marker = object()

    factory = NetworkMetadataAdapterFactory(
        coinex_client_factory=(
            lambda exchange: marker
        ),
    )

    adapter = factory.build(
        CoinExExchange()
    )

    assert isinstance(
        adapter,
        CoinExNetworkMetadataAdapter,
    )

    assert adapter._client is marker


def test_coinex_exchange_id_is_normalized():
    from exchanges.coinex_network_metadata_adapter import (
        CoinExNetworkMetadataAdapter,
    )

    class CoinExExchange:
        id = " COINEX "

    marker = object()

    factory = NetworkMetadataAdapterFactory(
        coinex_client_factory=(
            lambda exchange: marker
        ),
    )

    adapter = factory.build(
        CoinExExchange()
    )

    assert isinstance(
        adapter,
        CoinExNetworkMetadataAdapter,
    )


def test_default_factory_builds_coinex_network_adapter():
    from exchanges.coinex_network_metadata_adapter import (
        CoinExNetworkMetadataAdapter,
    )

    class CoinExExchange:
        id = "coinex"

    adapter = (
        NetworkMetadataAdapterFactory()
        .build(
            CoinExExchange()
        )
    )

    assert isinstance(
        adapter,
        CoinExNetworkMetadataAdapter,
    )


def test_phemex_builds_native_network_adapter():
    from exchanges.phemex_network_metadata_adapter import (
        PhemexNetworkMetadataAdapter,
    )

    class PhemexExchange:
        id = "phemex"

    marker = object()

    factory = NetworkMetadataAdapterFactory(
        phemex_client_factory=(
            lambda exchange: marker
        ),
    )

    adapter = factory.build(
        PhemexExchange()
    )

    assert isinstance(
        adapter,
        PhemexNetworkMetadataAdapter,
    )

    assert adapter._client is marker


def test_phemex_exchange_id_is_normalized():
    from exchanges.phemex_network_metadata_adapter import (
        PhemexNetworkMetadataAdapter,
    )

    class PhemexExchange:
        id = " PHEMEX "

    marker = object()

    factory = NetworkMetadataAdapterFactory(
        phemex_client_factory=(
            lambda exchange: marker
        ),
    )

    adapter = factory.build(
        PhemexExchange()
    )

    assert isinstance(
        adapter,
        PhemexNetworkMetadataAdapter,
    )


def test_default_factory_builds_phemex_network_adapter():
    from exchanges.phemex_network_metadata_adapter import (
        PhemexNetworkMetadataAdapter,
    )

    class PhemexExchange:
        id = "phemex"

    adapter = (
        NetworkMetadataAdapterFactory()
        .build(
            PhemexExchange()
        )
    )

    assert isinstance(
        adapter,
        PhemexNetworkMetadataAdapter,
    )


def test_okx_does_not_claim_native_public_network_metadata():
    from exchanges.ccxt_network_metadata_adapter import (
        CCXTNetworkMetadataAdapter,
    )

    class OKXExchange:
        id = "okx"

        def load_currencies(self):
            return {}

    adapter = (
        NetworkMetadataAdapterFactory()
        .build(
            OKXExchange()
        )
    )

    assert isinstance(
        adapter,
        CCXTNetworkMetadataAdapter,
    )


def test_binance_does_not_claim_native_public_network_metadata():
    from exchanges.ccxt_network_metadata_adapter import (
        CCXTNetworkMetadataAdapter,
    )

    class BinanceExchange:
        id = "binance"

        def load_currencies(self):
            return {}

    adapter = (
        NetworkMetadataAdapterFactory()
        .build(
            BinanceExchange()
        )
    )

    assert isinstance(
        adapter,
        CCXTNetworkMetadataAdapter,
    )


def test_builds_coinbase_native_network_adapter():
    from exchanges.coinbase_network_metadata_adapter import (
        CoinbaseNetworkMetadataAdapter,
    )

    class CoinbaseExchange:
        id = "coinbase"

    adapter = (
        NetworkMetadataAdapterFactory()
        .build(
            CoinbaseExchange()
        )
    )

    assert isinstance(
        adapter,
        CoinbaseNetworkMetadataAdapter,
    )


def test_coinbase_network_exchange_id_is_normalized():
    from exchanges.coinbase_network_metadata_adapter import (
        CoinbaseNetworkMetadataAdapter,
    )

    class CoinbaseExchange:
        id = " COINBASE "

    adapter = (
        NetworkMetadataAdapterFactory()
        .build(
            CoinbaseExchange()
        )
    )

    assert isinstance(
        adapter,
        CoinbaseNetworkMetadataAdapter,
    )
