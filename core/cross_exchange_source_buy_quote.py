"""
ArbOS™
EX-197
Cross-Exchange Source Buy Quote

Builds a one-leg, depth-aware paper buy quote on the
source exchange.

Converts starting USDT into the actual net coin amount
after source trading fee and slippage.

Paper valuation only.
No authentication.
No transfers.
No live orders.
"""

import math


class CrossExchangeSourceBuyQuote:
    def __init__(
        self,
        depth_scanner,
    ):
        if depth_scanner is None:
            raise ValueError(
                "depth_scanner is required"
            )

        self._depth_scanner = (
            depth_scanner
        )

    def quote(
        self,
        coin_asset,
        starting_usdt_value,
        source_fee_rate,
        max_slippage_percent,
    ):
        coin_asset = str(
            coin_asset
            or ""
        ).strip().upper()

        if not coin_asset:
            raise ValueError(
                "coin_asset is required"
            )

        if starting_usdt_value <= 0:
            raise ValueError(
                "starting_usdt_value "
                "must be positive"
            )

        route = {
            "route_id": (
                f"SOURCE-BUY-{coin_asset}"
            ),
            "legs": [
                {
                    "symbol": (
                        f"{coin_asset}/USDT"
                    ),
                    "side": "buy",
                },
            ],
        }

        scanned = (
            self._depth_scanner.scan_route(
                route=route,
                starting_value=(
                    starting_usdt_value
                ),
                fee_rate=source_fee_rate,
                max_slippage_percent=(
                    max_slippage_percent
                ),
            )
        )

        if scanned.get(
            "filled"
        ) is not True:
            return {
                **scanned,
                "coin_asset": coin_asset,
                "coin_amount": None,
                "starting_usdt_value": float(
                    starting_usdt_value
                ),
                "paper_only": True,
                "live_order_submitted": False,
            }

        if "net_final_value" not in scanned:
            return {
                **scanned,
                "filled": False,
                "reason": "source_buy_value_required",
                "coin_asset": coin_asset,
                "coin_amount": None,
                "starting_usdt_value": float(
                    starting_usdt_value
                ),
                "paper_only": True,
                "live_order_submitted": False,
            }

        raw_coin_amount = scanned[
            "net_final_value"
        ]

        try:
            coin_amount = float(
                raw_coin_amount
            )
        except (TypeError, ValueError):
            return {
                **scanned,
                "filled": False,
                "reason": "source_buy_value_invalid",
                "coin_asset": coin_asset,
                "coin_amount": None,
                "starting_usdt_value": float(
                    starting_usdt_value
                ),
                "paper_only": True,
                "live_order_submitted": False,
            }

        if (
            not math.isfinite(coin_amount)
            or coin_amount <= 0
        ):
            return {
                **scanned,
                "filled": False,
                "reason": "source_buy_value_invalid",
                "coin_asset": coin_asset,
                "coin_amount": None,
                "starting_usdt_value": float(
                    starting_usdt_value
                ),
                "paper_only": True,
                "live_order_submitted": False,
            }

        return {
            **scanned,
            "coin_asset": coin_asset,
            "coin_amount": coin_amount,
            "starting_usdt_value": float(
                starting_usdt_value
            ),
            "paper_only": True,
            "live_order_submitted": False,
        }
