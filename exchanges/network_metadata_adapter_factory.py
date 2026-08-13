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


class NetworkMetadataAdapterFactory:
    def __init__(
        self,
        weex_provider_factory=None,
    ):
        if weex_provider_factory is None:
            weex_provider_factory = (
                self._build_default_weex_provider
            )

        self._weex_provider_factory = (
            weex_provider_factory
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
