"""
ArbOS™
EX-075
Paper Route Decision Coordinator
"""

from exchanges.paper_route_pnl_integration import (
    PaperRoutePnLIntegration,
)
from exchanges.paper_route_profitability_gate import (
    PaperRouteProfitabilityGate,
)


class PaperRouteDecisionCoordinator:
    def __init__(self, market_data_provider):
        self._integration = PaperRoutePnLIntegration(
            market_data_provider
        )
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
        integrated = self._integration.execute(
            route=route,
            starting_value=starting_value,
            gross_final_value=gross_final_value,
            trading_fees=trading_fees,
            transfer_fees=transfer_fees,
            other_costs=other_costs,
            minimum_profit_percent=minimum_profit_percent,
        )

        gate_result = self._gate.evaluate(integrated["pnl"])

        record = {
            "route_id": integrated["route_id"],
            "execution": integrated["execution"],
            "pnl": integrated["pnl"],
            "accepted": gate_result["accepted"],
            "decision": (
                "ACCEPTED" if gate_result["accepted"] else "REJECTED"
            ),
            "reason": gate_result["reason"],
        }

        self._history.append(record)
        return record

    def history(self):
        return list(self._history)
