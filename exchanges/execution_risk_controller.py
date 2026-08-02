"""
ArbOS™
EX-029
Execution Risk Controller

Final safety gate before execution.

Validates:
- trade size
- expected profit
- liquidity
- slippage
- route validity
- approval status
"""


class ExecutionRiskController:

    def __init__(
        self,
        max_trade_size: float = 1000,
        min_profit: float = 1,
        min_liquidity: float = 100000,
        max_slippage: float = 2.0,
    ):
        self.max_trade_size = max_trade_size
        self.min_profit = min_profit
        self.min_liquidity = min_liquidity
        self.max_slippage = max_slippage

    def validate_execution(
        self,
        trade_size: float,
        expected_profit: float,
        liquidity: float,
        slippage: float,
        route_valid: bool,
        approval_status: str,
    ):
        if trade_size > self.max_trade_size:
            return {
                "status": "rejected",
                "reason": "trade_size_exceeded",
            }

        if expected_profit < self.min_profit:
            return {
                "status": "rejected",
                "reason": "profit_below_threshold",
            }

        if liquidity < self.min_liquidity:
            return {
                "status": "rejected",
                "reason": "insufficient_liquidity",
            }

        if slippage > self.max_slippage:
            return {
                "status": "rejected",
                "reason": "slippage_exceeded",
            }

        if not route_valid:
            return {
                "status": "rejected",
                "reason": "invalid_route",
            }

        if approval_status != "approved":
            return {
                "status": "rejected",
                "reason": "approval_required",
            }

        return {
            "status": "approved",
            "reason": "risk_checks_passed",
        }
