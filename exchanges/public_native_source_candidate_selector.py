"""
ArbOS™
EX-188
Public Native Source Candidate Selector

Selects one known public spot-market catalogue method from
the capability discovery result.

Selection only.
No authentication.
No transfers.
No live orders.
No public API calls.
"""


class PublicNativeSourceCandidateSelector:
    PREFERENCES = {
        "gate": (
            "publicSpotGetCurrencyPairs",
            "public_spot_get_currency_pairs",
        ),
        "bitget": (
            "publicSpotGetV2SpotPublicSymbols",
            "public_spot_get_v2_spot_public_symbols",
        ),
        "xt": (
            "publicSpotGetSymbol",
            "public_spot_get_symbol",
        ),
        "htx": (
            "publicGetCommonSymbols",
            "public_get_common_symbols",
        ),
        "kucoin": (
            "publicGetSymbols",
            "public_get_symbols",
        ),
        "digifinex": (
            "publicSpotGetMarketSymbols",
            "public_spot_get_market_symbols",
            "publicSpotGetSpotSymbols",
            "public_spot_get_spot_symbols",
            "publicSpotGetMarkets",
            "public_spot_get_markets",
        ),
    }

    def select(
        self,
        exchange_id,
        candidate_methods,
    ):
        if (
            exchange_id is None
            or not str(exchange_id).strip()
        ):
            raise ValueError(
                "exchange_id is required"
            )

        if candidate_methods is None:
            raise ValueError(
                "candidate_methods are required"
            )

        exchange_id = str(
            exchange_id
        ).strip().lower()

        candidates = set(
            str(method).strip()
            for method in candidate_methods
            if str(method).strip()
        )

        approved_methods = [
            method
            for method in self.PREFERENCES.get(
                exchange_id,
                (),
            )
            if method in candidates
        ]

        selected_method = (
            approved_methods[0]
            if approved_methods
            else None
        )

        return {
            "exchange_id": exchange_id,
            "selected_method": selected_method,
            "approved_methods": approved_methods,
            "approved_method_count": len(
                approved_methods
            ),
            "candidate_selected": (
                selected_method is not None
            ),
            "selection_complete": True,
            "public_api_called": False,
            "live_order_submitted": False,
        }
