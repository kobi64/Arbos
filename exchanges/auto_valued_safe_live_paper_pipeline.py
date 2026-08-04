"""
ArbOS™
EX-088
Auto-Valued Safe Live Paper Pipeline
"""

from exchanges.live_opportunity_route_builder import (
    LiveOpportunityRouteBuilder,
)
from exchanges.live_route_valuation_engine import (
    LiveRouteValuationEngine,
)
from exchanges.live_paper_execution_coordinator import (
    LivePaperExecutionCoordinator,
)


class AutoValuedSafeLivePaperPipeline:
    def __init__(self, market_data_provider):
        self._builder = LiveOpportunityRouteBuilder()
        self._valuation = LiveRouteValuationEngine(market_data_provider)
        self._coordinator = LivePaperExecutionCoordinator(market_data_provider)

    def execute(
        self,
        opportunity,
        starting_value,
        trading_fees,
        transfer_fees,
        other_costs,
        minimum_profit_percent,
    ):
        if opportunity is None:
            raise ValueError("opportunity is required")

        route = self._builder.build(opportunity)
        valuation = self._valuation.evaluate(
            route=route,
            starting_value=starting_value,
        )

        execution_legs = []

        for leg in valuation["legs"]:
            quantity = (
                leg["output_amount"]
                if leg["side"] == "buy"
                else leg["input_amount"]
            )

            execution_legs.append({
                "symbol": leg["symbol"],
                "side": leg["side"],
                "quantity": quantity,
            })

        execution_route = {
            "route_id": valuation["route_id"],
            "legs": execution_legs,
        }

        result = self._coordinator.execute(
            route=execution_route,
            starting_value=starting_value,
            gross_final_value=valuation["gross_final_value"],
            trading_fees=trading_fees,
            transfer_fees=transfer_fees,
            other_costs=other_costs,
            minimum_profit_percent=minimum_profit_percent,
        )

        record = dict(result)
        record["valuation"] = valuation
        return record
