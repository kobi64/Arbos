"""
ArbOS™
EX-079
Live Paper Execution Coordinator
"""

from exchanges.paper_arbitrage_route_execution import (
    PaperArbitrageRouteExecutionCoordinator,
)
from exchanges.paper_arbitrage_route_pnl import (
    PaperArbitrageRoutePnL,
)
from exchanges.paper_route_profitability_gate import (
    PaperRouteProfitabilityGate,
)


class LivePaperExecutionCoordinator:
    def __init__(self, market_data_provider):
        self._executor = PaperArbitrageRouteExecutionCoordinator(
            market_data_provider
        )
        self._pnl = PaperArbitrageRoutePnL()
        self._gate = PaperRouteProfitabilityGate()
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

        route_id = route.get("route_id")

        if route_id is None or not str(route_id).strip():
            raise ValueError("route_id is required")

        pnl = self._pnl.evaluate(
            starting_value=starting_value,
            gross_final_value=gross_final_value,
            trading_fees=trading_fees,
            transfer_fees=transfer_fees,
            other_costs=other_costs,
            minimum_profit_percent=minimum_profit_percent,
        )

        gate_result = self._gate.evaluate(pnl)

        execution = None

        if gate_result["accepted"]:
            execution = self._executor.execute(route)

        record = {
            "route_id": str(route_id).strip(),
            "pnl": pnl,
            "accepted": gate_result["accepted"],
            "decision": (
                "ACCEPTED"
                if gate_result["accepted"]
                else "REJECTED"
            ),
            "reason": gate_result["reason"],
            "execution": execution,
        }

        self._history.append(dict(record))
        return dict(record)

    def history(self):
        return [dict(record) for record in self._history]
