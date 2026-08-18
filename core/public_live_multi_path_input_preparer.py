"""
ArbOS™
EX-142
Public Live Multi-Path Input Preparer
"""

import math

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
from exchanges.network_identity_metadata_adapter_factory import (
    NetworkIdentityMetadataAdapterFactory,
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
        network_identity_metadata_adapter_factory=None,
        source_market_source=None,
        source_order_book_provider=None,
    ):
        self._source_exchange = source_exchange
        self._destination_exchange = destination_exchange
        self._source_buy_quote = source_buy_quote
        self._source_market_source = source_market_source
        self._source_order_book_provider = (
            source_order_book_provider
        )

        if network_metadata_adapter_factory is None:
            network_metadata_adapter_factory = (
                NetworkMetadataAdapterFactory()
            )

        self._network_metadata_adapter_factory = (
            network_metadata_adapter_factory
        )

        if (
            network_identity_metadata_adapter_factory
            is None
        ):
            network_identity_metadata_adapter_factory = (
                NetworkIdentityMetadataAdapterFactory()
            )

        self._network_identity_metadata_adapter_factory = (
            network_identity_metadata_adapter_factory
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
        try:
            starting_usdt_value = float(
                starting_usdt_value
            )
        except (TypeError, ValueError):
            raise ValueError(
                "starting_usdt_value must be positive"
            )

        if (
            not math.isfinite(starting_usdt_value)
            or starting_usdt_value <= 0
        ):
            raise ValueError(
                "starting_usdt_value must be positive"
            )

        try:
            source_fee_rate = float(
                source_fee_rate
            )
        except (TypeError, ValueError):
            raise ValueError(
                "source_fee_rate must be between 0 and 1"
            )

        if (
            not math.isfinite(source_fee_rate)
            or source_fee_rate < 0
            or source_fee_rate > 1
        ):
            raise ValueError(
                "source_fee_rate must be between 0 and 1"
            )

        try:
            max_slippage_percent = float(
                max_slippage_percent
            )
        except (TypeError, ValueError):
            raise ValueError(
                "max_slippage_percent must be non-negative"
            )

        if (
            not math.isfinite(max_slippage_percent)
            or max_slippage_percent < 0
        ):
            raise ValueError(
                "max_slippage_percent must be non-negative"
            )

        coin_asset = str(
            coin_asset
        ).strip().upper()

        if not coin_asset:
            raise ValueError(
                "coin_asset is required"
            )

        if self._source_market_source is not None:
            native_markets = (
                self._source_market_source.list_markets()
            )

            markets = {}

            for market in native_markets:
                if not isinstance(
                    market,
                    dict,
                ):
                    continue

                symbol = str(
                    market.get(
                        "symbol",
                        "",
                    )
                    or ""
                ).strip().upper()

                if not symbol:
                    continue

                markets[symbol] = {
                    **market,
                    "spot": True,
                }
        else:
            markets = (
                self._source_exchange.load_markets()
            )

        coin_symbol = f"{coin_asset}/USDT"

        if self._source_order_book_provider is None:
            source_snapshot = (
                LiveOrderBookSnapshotEngine(
                    self._source_exchange
                )
            )
        else:
            source_snapshot = None

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

            try:
                coin_amount = float(
                    source_buy_result.get(
                        "coin_amount"
                    )
                )
            except (TypeError, ValueError):
                raise ValueError(
                    "source buy coin_amount must be positive"
                )

            if (
                not math.isfinite(coin_amount)
                or coin_amount <= 0
            ):
                raise ValueError(
                    "source buy coin_amount must be positive"
                )

        else:
            if self._source_order_book_provider is not None:
                coin_book = (
                    self._source_order_book_provider.snapshot(
                        coin_symbol
                    )
                )
            else:
                coin_book = source_snapshot.snapshot(
                    coin_symbol
                )

            try:
                ask_price = float(
                    coin_book["asks"][0][0]
                )
            except (TypeError, ValueError, IndexError, KeyError):
                raise ValueError(
                    "source ask price must be positive"
                )

            if (
                not math.isfinite(ask_price)
                or ask_price <= 0
            ):
                raise ValueError(
                    "source ask price must be positive"
                )

            gross_coin_amount = (
                float(starting_usdt_value)
                / ask_price
            )

            coin_amount = (
                gross_coin_amount
                * (
                    1.0
                    - source_fee_rate
                )
            )

            if (
                not math.isfinite(coin_amount)
                or coin_amount <= 0
            ):
                raise ValueError(
                    "source buy coin_amount must be positive"
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
            self
            ._network_identity_metadata_adapter_factory
            .build(
                self._source_exchange
            )
        )

        destination_identity_adapter = (
            self
            ._network_identity_metadata_adapter_factory
            .build(
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

        if self._source_order_book_provider is not None:
            order_book_provider = (
                LiveOrderBookProviderAdapter(
                    self._source_order_book_provider
                )
            )
        else:
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

            try:
                output_amount = float(
                    quote["output_amount"]
                )
            except (TypeError, ValueError, KeyError):
                continue

            if (
                not math.isfinite(output_amount)
                or output_amount <= 0
            ):
                continue

            output_amount = (
                output_amount
                * (1.0 - source_fee_rate)
            )

            if (
                not math.isfinite(output_amount)
                or output_amount <= 0
            ):
                continue

            quote["output_amount"] = output_amount

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
            "source_network_identity_records": (
                source_network_identity_records
            ),
            "destination_network_identity_records": (
                destination_network_identity_records
            ),
            "bridge_quotes": bridge_quotes,
            "markets": markets,
            "paper_only": True,
            "live_order_submitted": False,
        }
