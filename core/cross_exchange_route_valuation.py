"""
ArbOS™
EX-137
Cross-Exchange Route Valuation
"""


class CrossExchangeRouteValuation:
    def __init__(self, destination_scanner):
        self._destination_scanner = destination_scanner

    def evaluate(
        self,
        candidate,
        starting_usdt_value,
        destination_fee_rate,
        max_slippage_percent,
    ):
        if candidate is None:
            raise ValueError("candidate is required")

        if starting_usdt_value <= 0:
            raise ValueError("starting_usdt_value must be positive")

        if candidate.get("executable") is not True:
            return {
                **candidate,
                "executable": False,
                "reason": candidate.get(
                    "reason",
                    "candidate_not_executable",
                ),
            }

        transfer_asset = str(
            candidate.get("transfer_asset", "")
        ).strip().upper()

        transfer_amount = float(
            candidate.get("transfer_amount", 0.0)
        )

        if not transfer_asset:
            raise ValueError("transfer_asset is required")

        if transfer_amount <= 0:
            raise ValueError("transfer_amount must be positive")

        route = {
            "route_id": candidate.get("route_id"),
            "legs": [
                {
                    "symbol": f"{transfer_asset}/USDT",
                    "side": "sell",
                },
            ],
        }

        scanned = self._destination_scanner.scan_route(
            route=route,
            starting_value=transfer_amount,
            fee_rate=destination_fee_rate,
            max_slippage_percent=max_slippage_percent,
        )

        if scanned.get("filled") is not True:
            return {
                **candidate,
                "executable": False,
                "reason": scanned.get(
                    "reason",
                    "destination_scan_failed",
                ),
                "destination_result": scanned,
            }

        net_final_value = float(
            scanned["net_final_value"]
        )

        net_profit = (
            net_final_value
            - float(starting_usdt_value)
        )

        net_profit_percent = (
            net_profit
            / float(starting_usdt_value)
        ) * 100.0

        return {
            **candidate,
            "executable": True,
            "net_final_value": net_final_value,
            "net_profit": net_profit,
            "net_profit_percent": net_profit_percent,
            "destination_result": scanned,
        }
