"""
ArbOS™
EX-134
Internal Multi-Bridge Scan Coordinator
"""


class InternalMultiBridgeScanCoordinator:
    def __init__(
        self,
        discovery,
        route_scanner,
        ranker,
    ):
        self._discovery = discovery
        self._route_scanner = route_scanner
        self._ranker = ranker

    def scan(
        self,
        markets,
        quote_asset,
        coin_asset,
        starting_value,
        fee_rate,
        max_slippage_percent,
    ):
        routes = self._discovery.discover(
            markets=markets,
            quote_asset=quote_asset,
            coin_asset=coin_asset,
        )

        results = []

        for route in routes:
            result = self._route_scanner.scan_route(
                route=route,
                starting_value=starting_value,
                fee_rate=fee_rate,
                max_slippage_percent=max_slippage_percent,
            )

            record = dict(result)

            if "bridge_asset" not in record:
                record["bridge_asset"] = route.get(
                    "bridge_asset"
                )

            results.append(record)

        filled_results = [
            result
            for result in results
            if result.get("filled") is True
        ]

        ranked_routes = self._ranker.rank(
            filled_results
        )

        best_route = (
            ranked_routes[0]
            if ranked_routes
            else None
        )

        return {
            "quote_asset": str(quote_asset).upper(),
            "coin_asset": str(coin_asset).upper(),
            "routes_discovered": len(routes),
            "routes_evaluated": len(results),
            "routes_filled": len(filled_results),
            "best_route": best_route,
            "ranked_routes": ranked_routes,
            "paper_only": True,
            "live_order_submitted": False,
        }
