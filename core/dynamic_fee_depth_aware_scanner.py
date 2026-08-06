"""
ArbOS™
EX-119
Dynamic Fee Depth-Aware Scanner
"""


class DynamicFeeDepthAwareScanner:
    def __init__(self, fee_resolver, depth_scanner):
        self._fee_resolver = fee_resolver
        self._depth_scanner = depth_scanner

    def scan_route(
        self,
        exchange_id,
        route,
        starting_value,
        max_slippage_percent,
        fee_type="taker",
    ):
        if exchange_id is None or not str(exchange_id).strip():
            raise ValueError("exchange_id is required")

        fee = self._fee_resolver.resolve(
            exchange_id=str(exchange_id).strip().lower(),
            fee_type=fee_type,
        )

        result = self._depth_scanner.scan_route(
            route=route,
            starting_value=starting_value,
            fee_rate=fee["fee_rate"],
            max_slippage_percent=max_slippage_percent,
        )

        record = dict(result)
        record["exchange_id"] = fee["exchange_id"]
        record["fee_type"] = fee["fee_type"]
        record["resolved_fee_rate"] = fee["fee_rate"]
        return record
