"""
ArbOS™
EX-191
Native Coverage Exchange Set Registry

Defines the configured public CCXT exchange set used by the
native coverage orchestration workflow.

Reuses the existing configurable venue registry and CCXT bootstrap.

Configuration/composition only.
No authentication.
No transfers.
No live orders.
"""

from core.ccxt_cex_venue_bootstrap import (
    CCXTCEXVenueBootstrap,
)
from core.configurable_cex_venue_registry import (
    ConfigurableCEXVenueRegistry,
)


class _NativeOnlyExchangeIdentity:
    def __init__(
        self,
        exchange_id,
    ):
        self.id = str(
            exchange_id
        ).strip().lower()


class NativeCoverageExchangeSetRegistry:
    NATIVE_ONLY_EXCHANGE_IDS = {
        "ourbit",
    }

    DEFAULT_EXCHANGE_IDS = (
        "binance",
        "bingx",
        "bitget",
        "bitrue",
        "coinbase",
        "coinex",
        "digifinex",
        "gate",
        "htx",
        "kraken",
        "kucoin",
        "lbank",
        "mexc",
        "okx",
        "ourbit",
        "phemex",
        "poloniex",
        "toobit",
        "weex",
        "whitebit",
        "xt",
    )

    def __init__(
        self,
        ccxt_module,
        exchange_ids=None,
    ):
        if ccxt_module is None:
            raise ValueError(
                "ccxt_module is required"
            )

        self._registry = (
            ConfigurableCEXVenueRegistry()
        )

        bootstrap = CCXTCEXVenueBootstrap(
            ccxt_module
        )

        selected_ids = (
            list(exchange_ids)
            if exchange_ids is not None
            else list(
                self.DEFAULT_EXCHANGE_IDS
            )
        )

        ccxt_exchange_ids = []
        native_only_exchange_ids = []

        for exchange_id in selected_ids:
            normalized = str(
                exchange_id
            ).strip().lower()

            if (
                normalized
                in self.NATIVE_ONLY_EXCHANGE_IDS
            ):
                native_only_exchange_ids.append(
                    normalized
                )
            else:
                ccxt_exchange_ids.append(
                    normalized
                )

        bootstrap.register_venues(
            registry=self._registry,
            exchange_ids=ccxt_exchange_ids,
            enabled=True,
        )

        for exchange_id in native_only_exchange_ids:
            self._registry.register(
                exchange_id=exchange_id,
                factory=(
                    lambda exchange_id=exchange_id: (
                        _NativeOnlyExchangeIdentity(
                            exchange_id
                        )
                    )
                ),
                enabled=True,
            )

        self.live_order_submitted = False

    def enabled_exchange_ids(self):
        return (
            self._registry
            .enabled_exchange_ids()
        )

    def set_enabled(
        self,
        exchange_id,
        enabled,
    ):
        self._registry.set_enabled(
            exchange_id,
            enabled,
        )

    def build_exchange_map(self):
        return {
            exchange_id: (
                self._registry.create(
                    exchange_id
                )
            )
            for exchange_id in (
                self.enabled_exchange_ids()
            )
        }
