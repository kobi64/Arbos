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

from exchanges.mexc_network_identity_metadata_adapter import (
    MexcNetworkIdentityMetadataAdapter,
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

from exchanges.lbank_network_identity_metadata_adapter import (
    LBankNetworkIdentityMetadataAdapter,
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


class NetworkIdentityMetadataAdapterFactory:
    def __init__(
        self,
        poloniex_provider_factory=None,
        mexc_provider_factory=None,
        lbank_provider_factory=None,
    ):
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

        if lbank_provider_factory is None:
            lbank_provider_factory = (
                self._build_default_lbank_provider
            )

        self._lbank_provider_factory = (
            lbank_provider_factory
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

        if exchange_id == "mexc":
            provider = (
                self._mexc_provider_factory(
                    exchange
                )
            )

            return (
                MexcNetworkIdentityMetadataAdapter(
                    provider=provider,
                )
            )

        if exchange_id == "lbank":
            provider = (
                self._lbank_provider_factory(
                    exchange
                )
            )

            return (
                LBankNetworkIdentityMetadataAdapter(
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
    def _build_default_lbank_provider(
        exchange,
    ):
        return LBankVerificationProvider(
            client=LBankNetworkMetadataClient(),
            normalizer=LBankNetworkNormalizer(),
        )
