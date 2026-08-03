"""
ArbOS™
EX-071
Paper Arbitrage Route Execution Coordinator
"""

from exchanges.live_market_paper_bridge import LiveMarketPaperBridge


class PaperArbitrageRouteExecutionCoordinator:
    def __init__(self, market_data_provider):
        self._bridge = LiveMarketPaperBridge(market_data_provider)
        self._history = []

    def execute(self, route):
        if route is None:
            raise ValueError("route is required")

        route_id = route.get("route_id")

        if route_id is None or not str(route_id).strip():
            raise ValueError("route_id is required")

        legs = route.get("legs")

        if not legs:
            raise ValueError("legs are required")

        executed_legs = []

        for index, leg in enumerate(legs, start=1):
            order = {
                "symbol": leg.get("symbol"),
                "side": leg.get("side"),
                "order_type": leg.get("order_type", "market"),
                "quantity": leg.get("quantity"),
            }

            result = self._bridge.execute(order)
            result["leg_number"] = index
            executed_legs.append(result)

        record = {
            "route_id": str(route_id).strip(),
            "status": "COMPLETED",
            "legs": executed_legs,
        }

        self._history.append(dict(record))
        return dict(record)

    def history(self):
        return [dict(record) for record in self._history]
