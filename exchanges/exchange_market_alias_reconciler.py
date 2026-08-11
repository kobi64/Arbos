"""
ArbOS™
EX-185
Exchange Market Alias Reconciler

Reconciles CCXT-normalized market symbols with exchange-native
market symbols using exchange-native market identity.

An alias is accepted only when:
- the CCXT market is active spot,
- the normalized symbols differ, and
- the CCXT native market id exactly matches the native raw symbol.

Research/public market-data infrastructure only.
No authentication.
No transfers.
No live orders.
"""


class ExchangeMarketAliasReconciler:
    def reconcile(
        self,
        ccxt_markets,
        native_markets,
    ):
        if ccxt_markets is None:
            raise ValueError(
                "ccxt_markets is required"
            )

        if native_markets is None:
            raise ValueError(
                "native_markets is required"
            )

        native_by_id = {}

        for market in native_markets:
            if not isinstance(market, dict):
                continue

            symbol = self._normalize_symbol(
                market.get("symbol")
            )

            raw = market.get("raw") or {}

            native_id = self._normalize_id(
                raw.get("symbol")
            )

            if not symbol or not native_id:
                continue

            native_by_id[native_id] = symbol

        alias_matches = []

        for ccxt_symbol, market in (
            ccxt_markets.items()
        ):
            if not isinstance(market, dict):
                continue

            if market.get("spot") is not True:
                continue

            if market.get(
                "active",
                True,
            ) is False:
                continue

            normalized_ccxt_symbol = (
                self._normalize_symbol(
                    ccxt_symbol
                )
            )

            native_id = self._normalize_id(
                market.get("id")
            )

            if (
                not normalized_ccxt_symbol
                or not native_id
            ):
                continue

            native_symbol = native_by_id.get(
                native_id
            )

            if not native_symbol:
                continue

            if (
                native_symbol
                == normalized_ccxt_symbol
            ):
                continue

            alias_matches.append({
                "ccxt_symbol": (
                    normalized_ccxt_symbol
                ),
                "native_symbol": (
                    native_symbol
                ),
                "native_market_id": (
                    native_id
                ),
            })

        alias_matches = sorted(
            alias_matches,
            key=lambda item: (
                item["ccxt_symbol"],
                item["native_symbol"],
            ),
        )

        return {
            "alias_match_count": len(
                alias_matches
            ),
            "alias_matches": alias_matches,
            "reconciliation_complete": True,
            "live_order_submitted": False,
        }

    @staticmethod
    def _normalize_symbol(value):
        if value is None:
            return None

        symbol = str(
            value
        ).strip().upper()

        return symbol or None

    @staticmethod
    def _normalize_id(value):
        if value is None:
            return None

        market_id = str(
            value
        ).strip().upper()

        return market_id or None
