"""
ArbOS™
EX-218
Network Identity Metadata Adapter Factory

Builds the appropriate network identity metadata adapter
for an exchange.

Current policy:
- Poloniex -> native Poloniex identity adapter
- all other exchanges -> CCXT identity adapter

Read-only.
No transfers.
No live orders.
"""

from exchanges.ccxt_network_identity_metadata_adapter import (
    CCXTNetworkIdentityMetadataAdapter,
)
from exchanges.poloniex_network_identity_metadata_adapter import (
    PoloniexNetworkIdentityMetadataAdapter,
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


class NetworkIdentityMetadataAdapterFactory:
    def __init__(
        self,
        poloniex_provider_factory=None,
    ):
        if poloniex_provider_factory is None:
            poloniex_provider_factory = (
                self._build_default_poloniex_provider
            )

        self._poloniex_provider_factory = (
            poloniex_provider_factory
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

        if exchange_id == "poloniex":
            provider = (
                self._poloniex_provider_factory(
                    exchange
                )
            )

            return (
                PoloniexNetworkIdentityMetadataAdapter(
                    provider=provider,
                )
            )

        return (
            CCXTNetworkIdentityMetadataAdapter(
                exchange
            )
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
