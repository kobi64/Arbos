"""
ArbOS™
EX-140
Live Multi-Path Paper Scan
"""

from core.profitable_opportunity_selector import (
    ProfitableOpportunitySelector,
)


class LiveMultiPathPaperScan:
    def __init__(
        self,
        internal_scanner,
        integration_coordinator,
    ):
        self._internal_scanner = internal_scanner
        self._integration_coordinator = integration_coordinator

    def scan(
        self,
        markets,
        quote_asset,
        coin_asset,
        starting_value,
        fee_rate,
        destination_fee_rate,
        max_slippage_percent,
        cross_exchange_generate_kwargs,
        minimum_profit_percent=0.0,
    ):
        internal = self._internal_scanner.scan(
            markets=markets,
            quote_asset=quote_asset,
            coin_asset=coin_asset,
            starting_value=starting_value,
            fee_rate=fee_rate,
            max_slippage_percent=max_slippage_percent,
        )

        internal_routes = internal.get(
            "ranked_routes",
            [],
        )

        result = self._integration_coordinator.evaluate(
            internal_routes=internal_routes,
            cross_exchange_generate_kwargs=cross_exchange_generate_kwargs,
            starting_usdt_value=starting_value,
            destination_fee_rate=destination_fee_rate,
            max_slippage_percent=max_slippage_percent,
        )

        profitability = (
            ProfitableOpportunitySelector().select(
                routes=result.get(
                    "ranked_routes",
                    [],
                ),
                starting_value=starting_value,
                minimum_profit_percent=(
                    minimum_profit_percent
                ),
            )
        )

        return {
            **result,
            **profitability,
            "internal_best_route": internal.get(
                "best_route"
            ),
            "minimum_profit_percent": (
                minimum_profit_percent
            ),
            "paper_only": True,
            "live_order_submitted": False,
        }
