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
            pre_transfer_amount = float(
                candidate.get(
                    "pre_transfer_amount",
                    0.0,
                )
            )

            if pre_transfer_amount <= 0:
                return {
                    **candidate,
                    "executable": False,
                    "reason": candidate.get(
                        "reason",
                        "candidate_not_executable",
                    ),
                    "valuation_only": False,
                    "paper_market_value_available": False,
                }

            transfer_asset = str(
                candidate.get(
                    "transfer_asset",
                    "",
                )
            ).strip().upper()

            if not transfer_asset:
                return {
                    **candidate,
                    "executable": False,
                    "reason": candidate.get(
                        "reason",
                        "candidate_not_executable",
                    ),
                    "valuation_only": False,
                    "paper_market_value_available": False,
                }

            route = {
                "route_id": candidate.get(
                    "route_id"
                ),
                "legs": [
                    {
                        "symbol": (
                            f"{transfer_asset}/USDT"
                        ),
                        "side": "sell",
                    },
                ],
            }

            try:
                scanned = (
                    self._destination_scanner.scan_route(
                        route=route,
                        starting_value=(
                            pre_transfer_amount
                        ),
                        fee_rate=(
                            destination_fee_rate
                        ),
                        max_slippage_percent=(
                            max_slippage_percent
                        ),
                    )
                )
            except Exception as exc:
                return {
                    **candidate,
                    "executable": False,
                    "reason": candidate.get(
                        "reason",
                        "candidate_not_executable",
                    ),
                    "valuation_only": True,
                    "paper_market_value_available": False,
                    "destination_error": (
                        f"{type(exc).__name__}: {exc}"
                    ),
                    "paper_only": True,
                    "live_order_submitted": False,
                }

            if scanned.get("filled") is not True:
                return {
                    **candidate,
                    "executable": False,
                    "reason": candidate.get(
                        "reason",
                        "candidate_not_executable",
                    ),
                    "valuation_only": True,
                    "paper_market_value_available": False,
                    "hypothetical_destination_result": (
                        scanned
                    ),
                }

            hypothetical_final_value = float(
                scanned["net_final_value"]
            )

            hypothetical_profit = (
                hypothetical_final_value
                - float(starting_usdt_value)
            )

            hypothetical_profit_percent = (
                hypothetical_profit
                / float(starting_usdt_value)
            ) * 100.0

            return {
                **candidate,
                "executable": False,
                "reason": candidate.get(
                    "reason",
                    "candidate_not_executable",
                ),
                "valuation_only": True,
                "paper_market_value_available": True,
                "hypothetical_transfer_amount": (
                    pre_transfer_amount
                ),
                "hypothetical_final_value": (
                    hypothetical_final_value
                ),
                "hypothetical_profit": (
                    hypothetical_profit
                ),
                "hypothetical_profit_percent": (
                    hypothetical_profit_percent
                ),
                "hypothetical_destination_result": (
                    scanned
                ),
                "transfer_verified": False,
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

        try:
            scanned = (
                self._destination_scanner.scan_route(
                    route=route,
                    starting_value=transfer_amount,
                    fee_rate=destination_fee_rate,
                    max_slippage_percent=(
                        max_slippage_percent
                    ),
                )
            )
        except Exception as exc:
            return {
                **candidate,
                "executable": False,
                "reason": (
                    "destination_market_unavailable"
                ),
                "destination_result": None,
                "destination_error": (
                    f"{type(exc).__name__}: {exc}"
                ),
                "paper_only": True,
                "live_order_submitted": False,
            }

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

        destination_result = dict(scanned)

        destination_result.pop(
            "net_profit",
            None,
        )
        destination_result.pop(
            "net_profit_percent",
            None,
        )

        destination_result["input_asset"] = (
            transfer_asset
        )
        destination_result["output_asset"] = "USDT"
        destination_result["pnl_comparable"] = False

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
            "destination_result": destination_result,
        }
