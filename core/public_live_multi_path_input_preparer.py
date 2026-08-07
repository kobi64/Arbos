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
    ):
        self._source_exchange = source_exchange
        self._destination_exchange = destination_exchange

    def prepare(
        self,
        source_exchange_id,
        destination_exchange_id,
        coin_asset,
        starting_usdt_value,
        source_fee_rate,
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
            * (1.0 - float(source_fee_rate))
        )

        source_network_adapter = (
            CCXTNetworkMetadataAdapter(
                self._source_exchange
            )
        )

        destination_network_adapter = (
            CCXTNetworkMetadataAdapter(
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
            "destination_exchange": (
                destination_exchange_id
            ),
            "coin_asset": coin_asset,
            "coin_amount": coin_amount,
            "source_networks": source_networks,
            "destination_networks": (
                destination_networks
            ),
            "bridge_quotes": bridge_quotes,
            "markets": markets,
        }
