"""
ArbOS™
EX-217
Network Metadata Adapter Factory

Builds the appropriate network metadata adapter for an exchange.

Current policy:
- WEEX -> WeexNetworkMetadataAdapter
- all other exchanges -> CCXTNetworkMetadataAdapter

This provides a generic extension point for future native
network metadata providers such as MEXC, BingX, Poloniex, etc.

Read-only.
No transfers.
No live orders.
"""

from exchanges.ccxt_network_metadata_adapter import (
    CCXTNetworkMetadataAdapter,
)
from exchanges.weex_network_metadata_adapter import (
    WeexNetworkMetadataAdapter,
)
from exchanges.weex_public_spot_client import (
    WeexPublicSpotClient,
)
from exchanges.weex_network_normalizer import (
    WeexNetworkNormalizer,
)
from exchanges.weex_verification_adapter import (
    WeexVerificationAdapter,
)
from exchanges.weex_verification_provider import (
    WeexVerificationProvider,
)

from exchanges.poloniex_network_metadata_adapter import (
    PoloniexNetworkMetadataAdapter,
)
from exchanges.poloniex_public_spot_client import (
    PoloniexPublicSpotClient,
)
from exchanges.poloniex_network_normalizer import (
    PoloniexNetworkNormalizer,
)
from exchanges.poloniex_verification_provider import (
    PoloniexVerificationProvider,
)

from exchanges.mexc_network_metadata_adapter import (
    MexcNetworkMetadataAdapter,
)
from exchanges.mexc_wallet_metadata_client import (
    MexcWalletMetadataClient,
)
from exchanges.mexc_network_normalizer import (
    MexcNetworkNormalizer,
)
from exchanges.mexc_verification_provider import (
    MexcVerificationProvider,
)

from exchanges.ourbit_network_metadata_adapter import (
    OurbitNetworkMetadataAdapter,
)
from exchanges.ourbit_wallet_metadata_client import (
    OurbitWalletMetadataClient,
)

from exchanges.lbank_network_metadata_adapter import (
    LBankNetworkMetadataAdapter,
)
from exchanges.lbank_network_metadata_client import (
    LBankNetworkMetadataClient,
)
from exchanges.lbank_network_normalizer import (
    LBankNetworkNormalizer,
)
from exchanges.lbank_verification_provider import (
    LBankVerificationProvider,
)

from exchanges.bingx_network_metadata_adapter import (
    BingXNetworkMetadataAdapter,
)
from exchanges.bingx_wallet_metadata_client import (
    BingXWalletMetadataClient,
)

from exchanges.kraken_network_metadata_adapter import (
    KrakenNetworkMetadataAdapter,
)
from exchanges.kraken_wallet_metadata_client import (
    KrakenWalletMetadataClient,
)

from exchanges.gateio_network_metadata_adapter import (
    GateIONetworkMetadataAdapter,
)
from exchanges.gateio_wallet_metadata_client import (
    GateIOWalletMetadataClient,
)


class NetworkMetadataAdapterFactory:
    def __init__(
        self,
        weex_provider_factory=None,
        poloniex_provider_factory=None,
        mexc_provider_factory=None,
        ourbit_client_factory=None,
        lbank_provider_factory=None,
        bingx_client_factory=None,
        kraken_client_factory=None,
        gateio_client_factory=None,
    ):
        if weex_provider_factory is None:
            weex_provider_factory = (
                self._build_default_weex_provider
            )

        self._weex_provider_factory = (
            weex_provider_factory
        )

        if poloniex_provider_factory is None:
            poloniex_provider_factory = (
                self._build_default_poloniex_provider
            )

        self._poloniex_provider_factory = (
            poloniex_provider_factory
        )

        if mexc_provider_factory is None:
            mexc_provider_factory = (
                self._build_default_mexc_provider
            )

        self._mexc_provider_factory = (
            mexc_provider_factory
        )

        if ourbit_client_factory is None:
            ourbit_client_factory = (
                self._build_default_ourbit_client
            )

        self._ourbit_client_factory = (
            ourbit_client_factory
        )

        if lbank_provider_factory is None:
            lbank_provider_factory = (
                self._build_default_lbank_provider
            )

        self._lbank_provider_factory = (
            lbank_provider_factory
        )

        if bingx_client_factory is None:
            bingx_client_factory = (
                self._build_default_bingx_client
            )

        self._bingx_client_factory = (
            bingx_client_factory
        )

        if kraken_client_factory is None:
            kraken_client_factory = (
                self._build_default_kraken_client
            )

        self._kraken_client_factory = (
            kraken_client_factory
        )

        if gateio_client_factory is None:
            gateio_client_factory = (
                self._build_default_gateio_client
            )

        self._gateio_client_factory = (
            gateio_client_factory
        )

    def build(
        self,
        exchange,
    ):
        if exchange is None:
            raise ValueError(
                "exchange is required"
            )

        exchange_id = str(
            getattr(
                exchange,
                "id",
                "",
            )
            or ""
        ).strip().lower()

        if exchange_id == "weex":
            provider = (
                self._weex_provider_factory(
                    exchange
                )
            )

            return (
                WeexNetworkMetadataAdapter(
                    provider=provider,
                )
            )

        if exchange_id == "poloniex":
            provider = (
                self._poloniex_provider_factory(
                    exchange
                )
            )

            return (
                PoloniexNetworkMetadataAdapter(
                    provider=provider,
                )
            )

        if exchange_id == "mexc":
            provider = (
                self._mexc_provider_factory(
                    exchange
                )
            )

            return (
                MexcNetworkMetadataAdapter(
                    provider=provider,
                )
            )

        if exchange_id == "ourbit":
            client = (
                self._ourbit_client_factory(
                    exchange
                )
            )

            return (
                OurbitNetworkMetadataAdapter(
                    client=client,
                )
            )

        if exchange_id == "lbank":
            provider = (
                self._lbank_provider_factory(
                    exchange
                )
            )

            return (
                LBankNetworkMetadataAdapter(
                    provider=provider,
                )
            )

        if exchange_id == "bingx":
            client = (
                self._bingx_client_factory(
                    exchange
                )
            )

            return (
                BingXNetworkMetadataAdapter(
                    client=client,
                )
            )

        if exchange_id == "kraken":
            client = (
                self._kraken_client_factory(
                    exchange
                )
            )

            return (
                KrakenNetworkMetadataAdapter(
                    client=client,
                )
            )

        if exchange_id == "gateio":
            client = (
                self._gateio_client_factory(
                    exchange
                )
            )

            return (
                GateIONetworkMetadataAdapter(
                    client=client,
                )
            )

        return CCXTNetworkMetadataAdapter(
            exchange
        )

    @staticmethod
    def _build_default_weex_provider(
        exchange,
    ):
        return WeexVerificationProvider(
            client=WeexPublicSpotClient(),
            adapter=WeexVerificationAdapter(
                network_normalizer=(
                    WeexNetworkNormalizer()
                )
            ),
        )

    @staticmethod
    def _build_default_poloniex_provider(
        exchange,
    ):
        return PoloniexVerificationProvider(
            client=PoloniexPublicSpotClient(),
            normalizer=(
                PoloniexNetworkNormalizer()
            ),
        )

    @staticmethod
    def _build_default_mexc_provider(
        exchange,
    ):
        return MexcVerificationProvider(
            client=MexcWalletMetadataClient(
                api_key=None,
                api_secret=None,
            ),
            normalizer=MexcNetworkNormalizer(),
        )

    @staticmethod
    def _build_default_ourbit_client(
        exchange,
    ):
        return OurbitWalletMetadataClient(
            api_key=None,
            api_secret=None,
        )

    @staticmethod
    def _build_default_lbank_provider(
        exchange,
    ):
        return LBankVerificationProvider(
            client=LBankNetworkMetadataClient(),
            normalizer=LBankNetworkNormalizer(),
        )

    @staticmethod
    def _build_default_bingx_client(
        exchange,
    ):
        return BingXWalletMetadataClient(
            api_key=None,
            api_secret=None,
        )

    @staticmethod
    def _build_default_kraken_client(
        exchange,
    ):
        return KrakenWalletMetadataClient(
            api_key=None,
            api_secret=None,
        )

    @staticmethod
    def _build_default_gateio_client(
        exchange,
    ):
        return GateIOWalletMetadataClient(
            api_key=None,
            api_secret=None,
        )
