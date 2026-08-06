"""
ArbOS™
EX-127
Venue-Aware Dynamic Fee Depth Scanner
"""


class VenueAwareDynamicFeeDepthScanner:
    def __init__(self, fee_resolver, depth_scanners):
        self._fee_resolver = fee_resolver
        self._depth_scanners = {
            str(exchange_id).strip().lower(): scanner
            for exchange_id, scanner in depth_scanners.items()
        }

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

        normalized = str(exchange_id).strip().lower()

        depth_scanner = self._depth_scanners.get(normalized)

        if depth_scanner is None:
            raise ValueError("venue depth scanner not found")

        fee = self._fee_resolver.resolve(
            exchange_id=normalized,
            fee_type=fee_type,
        )

        result = depth_scanner.scan_route(
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
