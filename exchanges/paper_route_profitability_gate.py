"""
ArbOS™
EX-074
Paper Route Profitability Gate
"""


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

        return {
            "accepted": bool(pnl_result["profitable"]),
            "net_profit": pnl_result["net_profit"],
            "profit_percent": pnl_result["profit_percent"],
            "reason": pnl_result.get("reason", ""),
        }
