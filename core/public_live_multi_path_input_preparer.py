"""
ArbOS™
EX-142
Public Live Multi-Path Input Preparer
"""

from core.live_order_book_provider_adapter import (
    LiveOrderBookProviderAdapter,
)
from core.order_book_spot_conversion_quote_provider import (
    OrderBookSpotConversionQuoteProvider,
)
from exchanges.ccxt_network_metadata_adapter import (
    CCXTNetworkMetadataAdapter,
)
from exchanges.network_metadata_adapter_factory import (
    NetworkMetadataAdapterFactory,
)
from exchanges.ccxt_network_identity_metadata_adapter import (
    CCXTNetworkIdentityMetadataAdapter,
)
from exchanges.live_order_book_snapshot_engine import (
    LiveOrderBookSnapshotEngine,
)
from exchanges.order_book_liquidity_slippage_engine import (
    OrderBookLiquiditySlippageEngine,
)


class PublicLiveMultiPathInputPreparer:
    def __init__(
        self,
        source_exchange,
        destination_exchange,
        source_buy_quote=None,
        network_metadata_adapter_factory=None,
    ):
        self._source_exchange = source_exchange
        self._destination_exchange = destination_exchange
        self._source_buy_quote = source_buy_quote

        if network_metadata_adapter_factory is None:
            network_metadata_adapter_factory = (
                NetworkMetadataAdapterFactory()
            )

        self._network_metadata_adapter_factory = (
            network_metadata_adapter_factory
        )

    @staticmethod
    def _describe_network_metadata(
        adapter,
        coin,
        networks,
    ):
        describe = getattr(
            adapter,
            "describe_networks",
            None,
        )

        if callable(describe):
            result = dict(
                describe(
                    coin
                )
            )

            result.setdefault(
                "networks",
                networks,
            )

            result.setdefault(
                "network_metadata_available",
                bool(networks),
            )

            result.setdefault(
                "transfer_verification_available",
                bool(
                    result.get(
                        "network_metadata_available"
                    )
                ),
            )

            result.setdefault(
                "network_metadata_reason",
                (
                    None
                    if result.get(
                        "network_metadata_available"
                    )
                    else "network_metadata_unavailable"
                ),
            )

            return result

        available = bool(
            networks
        )

        return {
            "coin": str(
                coin
            ).strip().upper(),
            "network_metadata_available": (
                available
            ),
            "network_metadata_reason": (
                None
                if available
                else "network_metadata_unavailable"
            ),
            "transfer_verification_available": (
                available
            ),
            "networks": networks,
            "paper_only": True,
            "live_order_submitted": False,
        }

    def prepare(
        self,
        source_exchange_id,
        destination_exchange_id,
        coin_asset,
        starting_usdt_value,
        source_fee_rate,
        max_slippage_percent=0.5,
    ):
        if starting_usdt_value <= 0:
            raise ValueError(
                "starting_usdt_value must be positive"
            )

        coin_asset = str(
            coin_asset
        ).strip().upper()

        if not coin_asset:
            raise ValueError(
                "coin_asset is required"
            )

        markets = self._source_exchange.load_markets()

        coin_symbol = f"{coin_asset}/USDT"

        source_snapshot = (
            LiveOrderBookSnapshotEngine(
                self._source_exchange
            )
        )

        source_buy_result = None
        source_buy_depth_aware = False

        if self._source_buy_quote is not None:
            source_buy_result = (
                self._source_buy_quote.quote(
                    coin_asset=coin_asset,
                    starting_usdt_value=(
                        starting_usdt_value
                    ),
                    source_fee_rate=(
                        source_fee_rate
                    ),
                    max_slippage_percent=(
                        max_slippage_percent
                    ),
                )
            )

            source_buy_depth_aware = True

            if source_buy_result.get(
                "filled"
            ) is not True:
                return {
                    "source_exchange": (
                        source_exchange_id
                    ),
                    "destination_exchange": (
                        destination_exchange_id
                    ),
                    "coin_asset": coin_asset,
                    "coin_amount": 0.0,
                    "prepare_complete": False,
                    "reason": (
                        "source_buy_"
                        + str(
                            source_buy_result.get(
                                "reason",
                                "failed",
                            )
                        )
                    ),
                    "source_buy_depth_aware": True,
                    "source_buy_result": (
                        source_buy_result
                    ),
                    "paper_only": True,
                    "live_order_submitted": False,
                }

            coin_amount = float(
                source_buy_result.get(
                    "coin_amount",
                    0.0,
                )
                or 0.0
            )

        else:
            coin_book = source_snapshot.snapshot(
                coin_symbol
            )

            ask_price = float(
                coin_book["asks"][0][0]
            )

            gross_coin_amount = (
                float(starting_usdt_value)
                / ask_price
            )

            coin_amount = (
                gross_coin_amount
                * (
                    1.0
                    - float(source_fee_rate)
                )
            )

        source_network_adapter = (
            self._network_metadata_adapter_factory.build(
                self._source_exchange
            )
        )

        destination_network_adapter = (
            self._network_metadata_adapter_factory.build(
                self._destination_exchange
            )
        )

        source_identity_adapter = (
            CCXTNetworkIdentityMetadataAdapter(
                self._source_exchange
            )
        )

        destination_identity_adapter = (
            CCXTNetworkIdentityMetadataAdapter(
                self._destination_exchange
            )
        )

        source_networks = {
            coin_asset: (
                source_network_adapter.get_networks(
                    coin_asset
                )
            )
        }

        destination_networks = {
            coin_asset: (
                destination_network_adapter.get_networks(
                    coin_asset
                )
            )
        }

        source_network_metadata = {
            coin_asset: (
                self._describe_network_metadata(
                    source_network_adapter,
                    coin_asset,
                    source_networks[
                        coin_asset
                    ],
                )
            )
        }

        destination_network_metadata = {
            coin_asset: (
                self._describe_network_metadata(
                    destination_network_adapter,
                    coin_asset,
                    destination_networks[
                        coin_asset
                    ],
                )
            )
        }

        source_network_metadata = {
            coin_asset: (
                self._describe_network_metadata(
                    source_network_adapter,
                    coin_asset,
                    source_networks[
                        coin_asset
                    ],
                )
            )
        }

        destination_network_metadata = {
            coin_asset: (
                self._describe_network_metadata(
                    destination_network_adapter,
                    coin_asset,
                    destination_networks[
                        coin_asset
                    ],
                )
            )
        }

        source_network_identity_records = {
            coin_asset: (
                source_identity_adapter.get_records(
                    coin_asset
                )
            )
        }

        destination_network_identity_records = {
            coin_asset: (
                destination_identity_adapter.get_records(
                    coin_asset
                )
            )
        }

        order_book_provider = (
            LiveOrderBookProviderAdapter(
                source_snapshot
            )
        )

        spot_provider = (
            OrderBookSpotConversionQuoteProvider(
                order_book_provider=order_book_provider,
                depth_engine=(
                    OrderBookLiquiditySlippageEngine()
                ),
            )
        )

        bridge_quotes = {}

        prefix = f"{coin_asset}/"

        for symbol, market in markets.items():
            if not market.get("spot", False):
                continue

            if market.get("active", True) is False:
                continue

            if not symbol.startswith(prefix):
                continue

            bridge_asset = symbol[
                len(prefix):
            ].strip().upper()

            if bridge_asset in {
                "",
                coin_asset,
                "USDT",
            }:
                continue

            bridge_usdt_symbol = (
                f"{bridge_asset}/USDT"
            )

            bridge_market = markets.get(
                bridge_usdt_symbol
            )

            if not bridge_market:
                continue

            if not bridge_market.get(
                "spot",
                False,
            ):
                continue

            source_networks[
                bridge_asset
            ] = (
                source_network_adapter.get_networks(
                    bridge_asset
                )
            )

            destination_networks[
                bridge_asset
            ] = (
                destination_network_adapter.get_networks(
                    bridge_asset
                )
            )

            source_network_metadata[
                bridge_asset
            ] = (
                self._describe_network_metadata(
                    source_network_adapter,
                    bridge_asset,
                    source_networks[
                        bridge_asset
                    ],
                )
            )

            destination_network_metadata[
                bridge_asset
            ] = (
                self._describe_network_metadata(
                    destination_network_adapter,
                    bridge_asset,
                    destination_networks[
                        bridge_asset
                    ],
                )
            )

            source_network_metadata[
                bridge_asset
            ] = (
                self._describe_network_metadata(
                    source_network_adapter,
                    bridge_asset,
                    source_networks[
                        bridge_asset
                    ],
                )
            )

            destination_network_metadata[
                bridge_asset
            ] = (
                self._describe_network_metadata(
                    destination_network_adapter,
                    bridge_asset,
                    destination_networks[
                        bridge_asset
                    ],
                )
            )

            source_network_identity_records[
                bridge_asset
            ] = (
                source_identity_adapter.get_records(
                    bridge_asset
                )
            )

            destination_network_identity_records[
                bridge_asset
            ] = (
                destination_identity_adapter.get_records(
                    bridge_asset
                )
            )

            quote = spot_provider.quote(
                from_asset=coin_asset,
                to_asset=bridge_asset,
                amount=coin_amount,
            )

            if quote is None:
                continue

            quote = dict(quote)

            quote["output_amount"] = (
                float(
                    quote["output_amount"]
                )
                * (1.0 - float(source_fee_rate))
            )

            bridge_quotes[
                bridge_asset
            ] = quote

        return {
            "source_exchange": (
                source_exchange_id
            ),
            "source_buy_depth_aware": (
                source_buy_depth_aware
            ),
            "source_buy_result": (
                source_buy_result
            ),
            "prepare_complete": True,
            "destination_exchange": (
                destination_exchange_id
            ),
            "coin_asset": coin_asset,
            "coin_amount": coin_amount,
            "source_networks": source_networks,
            "destination_networks": (
                destination_networks
            ),
            "source_network_metadata": (
                source_network_metadata
            ),
            "destination_network_metadata": (
                destination_network_metadata
            ),
            "source_network_metadata": (
                source_network_metadata
            ),
            "destination_network_metadata": (
                destination_network_metadata
            ),
            "source_network_identity_records": (
                source_network_identity_records
            ),
            "destination_network_identity_records": (
                destination_network_identity_records
            ),
            "bridge_quotes": bridge_quotes,
            "markets": markets,
        }
