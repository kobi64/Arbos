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
