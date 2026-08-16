"""
ArbOS™
EX-198
Live Coin Universe Selector

Selects liquid crypto assets from public exchange market
metadata for unified paper scanning.

Universe discovery does not require bulk ticker bid/ask data.
Actual route execution-quality validation remains the
responsibility of downstream order-book scanners.

Paper/public-data infrastructure only.
No authentication.
No transfers.
No live orders.
"""


class LiveCoinUniverseSelector:
    def __init__(
        self,
        excluded_assets=None,
    ):
        if excluded_assets is None:
            excluded_assets = {
                "USDT",
                "USDC",
                "USD",
            }

        self._excluded_assets = {
            str(asset).strip().upper()
            for asset in excluded_assets
            if str(asset).strip()
        }

    def select(
        self,
        exchange_id,
        markets,
        tickers,
        limit,
    ):
        if limit <= 0:
            raise ValueError(
                "limit must be positive"
            )

        exchange_id = str(
            exchange_id
            or ""
        ).strip().lower()

        markets = markets or {}
        tickers = tickers or {}

        ranked = []
        filtered_instrument_count = 0

        for symbol, market in markets.items():
            if market.get("spot") is not True:
                continue

            if market.get("active") is False:
                continue

            quote = str(
                market.get(
                    "quote",
                    "",
                )
                or ""
            ).strip().upper()

            if quote != "USDT":
                continue

            base = str(
                market.get(
                    "base",
                    "",
                )
                or ""
            ).strip().upper()

            if not base:
                continue

            if base in self._excluded_assets:
                continue

            if self._is_filtered_instrument(
                exchange_id=exchange_id,
                market=market,
            ):
                filtered_instrument_count += 1
                continue

            if self._is_leveraged_token(
                base=base,
            ):
                filtered_instrument_count += 1
                continue

            ticker = tickers.get(
                symbol,
                {},
            ) or {}

            quote_volume = ticker.get(
                "quoteVolume"
            )

            try:
                quote_volume = float(
                    quote_volume
                )
            except (
                TypeError,
                ValueError,
            ):
                continue

            if quote_volume <= 0:
                continue

            ranked.append({
                "coin_asset": base,
                "symbol": symbol,
                "quote_volume": (
                    quote_volume
                ),
            })

        ranked.sort(
            key=lambda item: (
                item["quote_volume"],
                item["coin_asset"],
            ),
            reverse=True,
        )

        selected = ranked[:limit]

        return {
            "exchange_id": exchange_id,
            "coin_assets": [
                item["coin_asset"]
                for item in selected
            ],
            "selected_markets": selected,
            "selected_count": len(
                selected
            ),
            "eligible_count": len(
                ranked
            ),
            "filtered_instrument_count": (
                filtered_instrument_count
            ),
            "bulk_bid_ask_required": False,
            "paper_only": True,
            "live_order_submitted": False,
        }

    @staticmethod
    def _is_leveraged_token(
        base,
    ):
        base = str(
            base
            or ""
        ).strip().upper()

        return base.endswith(
            (
                "3L",
                "3S",
                "5L",
                "5S",
            )
        )

    @staticmethod
    def _is_filtered_instrument(
        exchange_id,
        market,
    ):
        if exchange_id != "bitget":
            return False

        info = market.get(
            "info",
            {},
        ) or {}

        raw_base = str(
            info.get(
                "baseCoin",
                "",
            )
            or ""
        ).strip()

        # Bitget exposes a family of lowercase-r-prefixed
        # instruments such as rNVDA and rSPY. They should
        # not displace ordinary crypto assets in the
        # unified crypto scanning universe.
        #
        # Preserve genuine crypto assets whose canonical
        # symbol begins with uppercase R, e.g. RAY.
        return (
            len(raw_base) > 1
            and raw_base.startswith("r")
            and raw_base[1].isupper()
        )
