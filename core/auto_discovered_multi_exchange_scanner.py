"""
ArbOS™
EX-122
Auto-Discovered Multi-Exchange Scanner
"""


class AutoDiscoveredMultiExchangeScanner:
    def __init__(self, discovery, route_scanner):
        self._discovery = discovery
        self._route_scanner = route_scanner

    def scan(
        self,
        exchange_markets,
        quote_asset,
        bridge_asset,
        starting_value,
        max_slippage_percent,
        fee_type="taker",
    ):
        results = []

        for exchange_id, markets in exchange_markets.items():
            try:
                routes = self._discovery.discover(
                    markets=markets,
                    quote_asset=quote_asset,
                    bridge_asset=bridge_asset,
                )
            except Exception as exc:
                results.append({
                    "exchange_id": exchange_id,
                    "route_id": None,
                    "filled": False,
                    "reason": "venue_discovery_failed",
                    "error": f"{type(exc).__name__}: {exc}",
                    "paper_only": True,
                    "live_order_submitted": False,
                })
                continue

            for route in routes:
                try:
                    result = self._route_scanner.scan_route(
                        exchange_id=exchange_id,
                        route=route,
                        starting_value=starting_value,
                        max_slippage_percent=max_slippage_percent,
                        fee_type=fee_type,
                    )
                    results.append(dict(result))
                except Exception as exc:
                    results.append({
                        "exchange_id": exchange_id,
                        "route_id": route.get("route_id"),
                        "filled": False,
                        "reason": "route_scan_failed",
                        "error": f"{type(exc).__name__}: {exc}",
                        "paper_only": True,
                        "live_order_submitted": False,
                    })

        results.sort(
            key=lambda result: (
                result.get("filled", False),
                result.get("net_profit_percent", float("-inf")),
            ),
            reverse=True,
        )

        return results
