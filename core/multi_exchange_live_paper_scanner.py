"""
ArbOS™
EX-120
Multi-Exchange Live Paper Scanner
"""


class MultiExchangeLivePaperScanner:
    def __init__(self, exchange_scanner):
        self._exchange_scanner = exchange_scanner

    def scan(
        self,
        exchange_ids,
        route,
        starting_value,
        max_slippage_percent,
        fee_type="taker",
    ):
        if not exchange_ids:
            raise ValueError("exchange_ids are required")

        results = []

        for exchange_id in exchange_ids:
            try:
                result = self._exchange_scanner.scan_route(
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
                    "reason": "exchange_scan_failed",
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
