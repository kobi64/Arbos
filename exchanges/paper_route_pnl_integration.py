"""
ArbOS™
EX-073
Paper Route Execution + P&L Integration
"""

from exchanges.paper_arbitrage_route_execution import (
    PaperArbitrageRouteExecutionCoordinator,
)

from exchanges.paper_arbitrage_route_pnl import (
    PaperArbitrageRoutePnL,
)


class PaperRoutePnLIntegration:
    def __init__(self, market_data_provider):
        self._executor = PaperArbitrageRouteExecutionCoordinator(
            market_data_provider
        )
        self._pnl = PaperArbitrageRoutePnL()
        self._history = []

    def execute(
        self,
        route,
        starting_value,
        gross_final_value,
        trading_fees,
        transfer_fees,
        other_costs,
        minimum_profit_percent,
    ):
        if route is None:
            raise ValueError("route is required")

        execution = self._executor.execute(route)

        pnl = self._pnl.evaluate(
            starting_value=starting_value,
            gross_final_value=gross_final_value,
            trading_fees=trading_fees,
            transfer_fees=transfer_fees,
            other_costs=other_costs,
            minimum_profit_percent=minimum_profit_percent,
        )

        record = {
            "route_id": execution["route_id"],
            "execution": execution,
            "pnl": pnl,
        }

        self._history.append(record)
        return record

    def history(self):
        return list(self._history)
