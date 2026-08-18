"""
ArbOS™
EX-074
Paper Route Profitability Gate
"""


import math


class PaperRouteProfitabilityGate:
    def evaluate(self, pnl_result):
        if pnl_result is None:
            raise ValueError("pnl_result is required")
        if "profitable" not in pnl_result:
            raise ValueError("profitable is required")

        if "net_profit" not in pnl_result:
            raise ValueError("net_profit is required")

        if "profit_percent" not in pnl_result:
            raise ValueError("profit_percent is required")

        profitable = pnl_result["profitable"]

        if not isinstance(profitable, bool):
            raise ValueError(
                "profitable must be a boolean"
            )

        net_profit = self._finite_number(
            pnl_result["net_profit"],
            "net_profit",
        )
        profit_percent = self._finite_number(
            pnl_result["profit_percent"],
            "profit_percent",
        )

        if (
            profitable
            and (
                net_profit <= 0
                or profit_percent <= 0
            )
        ):
            return {
                "accepted": False,
                "net_profit": net_profit,
                "profit_percent": profit_percent,
                "reason": "invalid_profitable_economics",
            }

        return {
            "accepted": profitable,
            "net_profit": net_profit,
            "profit_percent": profit_percent,
            "reason": pnl_result.get("reason", ""),
        }

    @staticmethod
    def _finite_number(value, field):
        if isinstance(value, bool):
            raise ValueError(
                f"{field} must be a finite number"
            )

        try:
            number = float(value)
        except (
            TypeError,
            ValueError,
            OverflowError,
        ):
            raise ValueError(
                f"{field} must be a finite number"
            ) from None

        if not math.isfinite(number):
            raise ValueError(
                f"{field} must be a finite number"
            )

        return number
