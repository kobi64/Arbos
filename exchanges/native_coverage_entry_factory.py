"""
ArbOS™
EX-190
Native Coverage Entry Factory

Builds native coverage scanner entries from configured
exchange objects.

Configuration/composition only.
No authentication.
No transfers.
No live orders.
"""

from exchanges.bitget_native_market_source import (
    BitgetNativeMarketSource,
)
from exchanges.digifinex_native_market_source import (
    DigiFinexNativeMarketSource,
)
from exchanges.gate_native_market_source import (
    GateNativeMarketSource,
)
from exchanges.htx_native_market_source import (
    HTXNativeMarketSource,
)
from exchanges.kucoin_native_market_source import (
    KuCoinNativeMarketSource,
)
from exchanges.xt_native_market_source import (
    XTNativeMarketSource,
)


class NativeCoverageEntryFactory:
    def __init__(
        self,
        provider_factories=None,
        depth_sample_sizes=None,
        default_depth_sample_size=10,
    ):
        if (
            not isinstance(
                default_depth_sample_size,
                int,
            )
            or isinstance(
                default_depth_sample_size,
                bool,
            )
            or default_depth_sample_size <= 0
        ):
            raise ValueError(
                "default_depth_sample_size "
                "must be positive"
            )

        self._source_factories = {
            "bitget": BitgetNativeMarketSource,
            "digifinex": (
                DigiFinexNativeMarketSource
            ),
            "gate": GateNativeMarketSource,
            "htx": HTXNativeMarketSource,
            "kucoin": KuCoinNativeMarketSource,
            "xt": XTNativeMarketSource,
        }

        self._provider_factories = dict(
            provider_factories or {}
        )

        self._depth_sample_sizes = dict(
            depth_sample_sizes or {}
        )

        self._default_depth_sample_size = (
            default_depth_sample_size
        )

    def build(
        self,
        exchanges,
    ):
        if exchanges is None:
            raise ValueError(
                "exchanges are required"
            )

        entries = []
        unsupported_exchange_ids = []
        invalid_exchange_count = 0

        for exchange in exchanges.values():
            if exchange is None:
                invalid_exchange_count += 1
                continue

            exchange_id = str(
                getattr(
                    exchange,
                    "id",
                    "",
                )
                or ""
            ).strip().lower()

            if not exchange_id:
                invalid_exchange_count += 1
                continue

            source_factory = (
                self._source_factories.get(
                    exchange_id
                )
            )

            if source_factory is None:
                unsupported_exchange_ids.append(
                    exchange_id
                )
                continue

            entry = {
                "exchange": exchange,
                "native_market_source": (
                    source_factory(exchange)
                ),
            }

            provider_factory = (
                self._provider_factories.get(
                    exchange_id
                )
            )

            if provider_factory is not None:
                entry["order_book_provider"] = (
                    provider_factory(exchange)
                )

                sample_size = (
                    self._depth_sample_sizes.get(
                        exchange_id,
                        self._default_depth_sample_size,
                    )
                )

                entry["depth_sample_size"] = (
                    sample_size
                )

            entries.append(
                entry
            )

        return {
            "entry_count": len(entries),
            "entries": entries,
            "unsupported_exchange_count": len(
                unsupported_exchange_ids
            ),
            "unsupported_exchange_ids": (
                unsupported_exchange_ids
            ),
            "invalid_exchange_count": (
                invalid_exchange_count
            ),
            "build_complete": True,
            "live_order_submitted": False,
        }
