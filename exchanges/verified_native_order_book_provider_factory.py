"""
ArbOS™
EX-182 / EX-183 / EX-217
Verified Native Order Book Provider Factory

Selects the appropriate public order-book provider for an exchange.

Native fallback providers are supplied through the
NativeFallbackExchangeRegistry.

Unregistered exchanges continue using the normal CCXT snapshot engine.

Public market data / paper valuation only.
No authentication.
No transfers.
No live orders.
"""

from exchanges.live_order_book_snapshot_engine import (
    LiveOrderBookSnapshotEngine,
)
from exchanges.native_fallback_exchange_registry import (
    NativeFallbackExchangeRegistry,
)
from exchanges.verified_digifinex_order_book_provider import (
    VerifiedDigiFinexOrderBookProvider,
)
from exchanges.verified_kucoin_order_book_provider import (
    VerifiedKuCoinOrderBookProvider,
)
from exchanges.weex_native_order_book_provider import (
    WeexNativeOrderBookProvider,
)
from exchanges.weex_network_normalizer import (
    WeexNetworkNormalizer,
)
from exchanges.weex_public_spot_client import (
    WeexPublicSpotClient,
)
from exchanges.weex_verification_adapter import (
    WeexVerificationAdapter,
)
from exchanges.weex_verification_provider import (
    WeexVerificationProvider,
)

from exchanges.poloniex_public_spot_client import (
    PoloniexPublicSpotClient,
)
from exchanges.poloniex_verification_adapter import (
    PoloniexVerificationAdapter,
)
from exchanges.poloniex_native_order_book_provider import (
    PoloniexNativeOrderBookProvider,
)

from exchanges.mexc_public_spot_client import (
    MexcPublicSpotClient,
)
from exchanges.mexc_verification_adapter import (
    MexcVerificationAdapter,
)
from exchanges.mexc_native_order_book_provider import (
    MexcNativeOrderBookProvider,
)

from exchanges.ourbit_public_spot_client import (
    OurbitPublicSpotClient,
)
from exchanges.ourbit_verification_adapter import (
    OurbitVerificationAdapter,
)
from exchanges.ourbit_native_order_book_provider import (
    OurbitNativeOrderBookProvider,
)

from exchanges.lbank_public_spot_client import (
    LBankPublicSpotClient,
)
from exchanges.lbank_verification_adapter import (
    LBankVerificationAdapter,
)
from exchanges.lbank_native_order_book_provider import (
    LBankNativeOrderBookProvider,
)

from exchanges.bingx_public_spot_client import (
    BingXPublicSpotClient,
)
from exchanges.bingx_verification_adapter import (
    BingXVerificationAdapter,
)
from exchanges.bingx_native_order_book_provider import (
    BingXNativeOrderBookProvider,
)

from exchanges.kraken_public_spot_client import (
    KrakenPublicSpotClient,
)
from exchanges.kraken_verification_adapter import (
    KrakenVerificationAdapter,
)
from exchanges.kraken_native_order_book_provider import (
    KrakenNativeOrderBookProvider,
)

from exchanges.gateio_public_spot_client import (
    GateIOPublicSpotClient,
)
from exchanges.gateio_verification_adapter import (
    GateIOVerificationAdapter,
)
from exchanges.gateio_native_order_book_provider import (
    GateIONativeOrderBookProvider,
)



from exchanges.htx_public_spot_client import (
    HTXPublicSpotClient,
)
from exchanges.htx_verification_adapter import (
    HTXVerificationAdapter,
)
from exchanges.htx_native_order_book_provider import (
    HTXNativeOrderBookProvider,
)

from exchanges.bitget_public_spot_client import (
    BitgetPublicSpotClient,
)
from exchanges.bitget_verification_adapter import (
    BitgetVerificationAdapter,
)
from exchanges.bitget_native_order_book_provider import (
    BitgetNativeOrderBookProvider,
)


from exchanges.coinex_public_spot_client import (
    CoinExPublicSpotClient,
)
from exchanges.coinex_verification_adapter import (
    CoinExVerificationAdapter,
)
from exchanges.coinex_native_order_book_provider import (
    CoinExNativeOrderBookProvider,
)


from exchanges.phemex_public_spot_client import (
    PhemexPublicSpotClient,
)
from exchanges.phemex_verification_adapter import (
    PhemexVerificationAdapter,
)
from exchanges.phemex_native_order_book_provider import (
    PhemexNativeOrderBookProvider,
)
from exchanges.phemex_spot_scale_resolver import (
    PhemexSpotScaleResolver,
)


class VerifiedNativeOrderBookProviderFactory:
    def __init__(
        self,
        registry=None,
    ):
        if registry is None:
            registry = (
                NativeFallbackExchangeRegistry()
            )

            registry.register(
                "digifinex",
                lambda exchange: (
                    VerifiedDigiFinexOrderBookProvider(
                        exchange
                    )
                ),
            )

            registry.register(
                "kucoin",
                lambda exchange: (
                    VerifiedKuCoinOrderBookProvider(
                        exchange
                    )
                ),
            )

            registry.register(
                "weex",
                lambda exchange: (
                    WeexNativeOrderBookProvider(
                        provider=(
                            WeexVerificationProvider(
                                client=(
                                    WeexPublicSpotClient()
                                ),
                                adapter=(
                                    WeexVerificationAdapter(
                                        network_normalizer=(
                                            WeexNetworkNormalizer()
                                        )
                                    )
                                ),
                            )
                        )
                    )
                ),
            )

            registry.register(
                "poloniex",
                lambda exchange: (
                    PoloniexNativeOrderBookProvider(
                        client=(
                            PoloniexPublicSpotClient()
                        ),
                        adapter=(
                            PoloniexVerificationAdapter()
                        ),
                    )
                ),
            )

            registry.register(
                "mexc",
                lambda exchange: (
                    MexcNativeOrderBookProvider(
                        client=(
                            MexcPublicSpotClient()
                        ),
                        adapter=(
                            MexcVerificationAdapter()
                        ),
                    )
                ),
            )

            registry.register(
                "ourbit",
                lambda exchange: (
                    OurbitNativeOrderBookProvider(
                        client=(
                            OurbitPublicSpotClient()
                        ),
                        adapter=(
                            OurbitVerificationAdapter()
                        ),
                    )
                ),
            )

            registry.register(
                "lbank",
                lambda exchange: (
                    LBankNativeOrderBookProvider(
                        client=(
                            LBankPublicSpotClient()
                        ),
                        adapter=(
                            LBankVerificationAdapter()
                        ),
                    )
                ),
            )

            registry.register(
                "bingx",
                lambda exchange: (
                    BingXNativeOrderBookProvider(
                        adapter=(
                            BingXVerificationAdapter(
                                client=(
                                    BingXPublicSpotClient()
                                )
                            )
                        ),
                    )
                ),
            )

            registry.register(
                "kraken",
                lambda exchange: (
                    KrakenNativeOrderBookProvider(
                        adapter=(
                            KrakenVerificationAdapter(
                                client=(
                                    KrakenPublicSpotClient()
                                )
                            )
                        ),
                    )
                ),
            )

            registry.register(
                "gateio",
                lambda exchange: (
                    GateIONativeOrderBookProvider(
                        adapter=(
                            GateIOVerificationAdapter(
                                client=(
                                    GateIOPublicSpotClient()
                                )
                            )
                        ),
                    )
                ),
            )


            registry.register(
                "htx",
                lambda exchange: (
                    HTXNativeOrderBookProvider(
                        adapter=(
                            HTXVerificationAdapter(
                                client=(
                                    HTXPublicSpotClient()
                                )
                            )
                        ),
                    )
                ),
            )

            registry.register(
                "bitget",
                lambda exchange: (
                    BitgetNativeOrderBookProvider(
                        adapter=(
                            BitgetVerificationAdapter(
                                client=(
                                    BitgetPublicSpotClient()
                                )
                            )
                        ),
                    )
                ),
            )

        registry.register(
            "coinex",
            lambda exchange: (
                CoinExNativeOrderBookProvider(
                    adapter=(
                        CoinExVerificationAdapter(
                            client=(
                                CoinExPublicSpotClient()
                            )
                        )
                    ),
                )
            ),
        )

        registry.register(
            "phemex",
            lambda exchange: (
                self._build_phemex_provider()
            ),
        )

        self._registry = registry

    @staticmethod
    def _build_phemex_provider():
        client = PhemexPublicSpotClient()

        return PhemexNativeOrderBookProvider(
            adapter=(
                PhemexVerificationAdapter(
                    client=client,
                    scale_resolver=(
                        PhemexSpotScaleResolver(
                            client=client,
                        )
                    ),
                )
            ),
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

        provider = self._registry.build(
            exchange_id,
            exchange,
        )

        if provider is not None:
            return provider

        return LiveOrderBookSnapshotEngine(
            exchange
        )
