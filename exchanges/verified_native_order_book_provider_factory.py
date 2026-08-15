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

        self._registry = registry

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
