"""
ArbOS™
EX-080
Safe Live Paper Pipeline
"""

from exchanges.live_opportunity_route_builder import (
    LiveOpportunityRouteBuilder,
)
from exchanges.live_market_paper_route_adapter import (
    LiveMarketPaperRouteAdapter,
)
from exchanges.live_paper_execution_coordinator import (
    LivePaperExecutionCoordinator,
)


class SafeLivePaperPipeline:
    def __init__(self, market_data_provider):
        self._builder = LiveOpportunityRouteBuilder()
        self._adapter = LiveMarketPaperRouteAdapter(
            market_data_provider
        )
        self._coordinator = LivePaperExecutionCoordinator(
            market_data_provider
        )
        self._history = []

    def execute(
        self,
        opportunity,
        starting_value,
        gross_final_value,
        trading_fees,
        transfer_fees,
        other_costs,
        minimum_profit_percent,
    ):
        if opportunity is None:
            raise ValueError("opportunity is required")

        route = self._builder.build(opportunity)
        live_route = self._adapter.adapt(route)

        result = self._coordinator.execute(
            route=live_route,
            starting_value=starting_value,
            gross_final_value=gross_final_value,
            trading_fees=trading_fees,
            transfer_fees=transfer_fees,
            other_costs=other_costs,
            minimum_profit_percent=minimum_profit_percent,
        )

        self._history.append(dict(result))
        return dict(result)

    def history(self):
        return [dict(record) for record in self._history]
