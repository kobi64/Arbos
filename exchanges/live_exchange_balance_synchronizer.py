"""
ArbOS™
EX-097
Live Exchange Balance Synchronizer
"""


class LiveExchangeBalanceSynchronizer:
    def __init__(self, state_manager):
        self._state_manager = state_manager

    def sync(self, exchange, balance_response):
        if exchange is None or not str(exchange).strip():
            raise ValueError("exchange is required")

        if balance_response is None:
            raise ValueError("balance_response is required")

        exchange = str(exchange).strip()
        free = balance_response.get("free") or {}
        used = balance_response.get("used") or {}
        total = balance_response.get("total") or {}

        assets = set(free) | set(used) | set(total)
        balances = {}

        for asset in assets:
            free_amount = float(free.get(asset, 0.0) or 0.0)
            used_amount = float(used.get(asset, 0.0) or 0.0)
            total_amount = float(total.get(asset, 0.0) or 0.0)

            balances[asset] = {
                "free": free_amount,
                "used": used_amount,
                "total": total_amount,
            }

            self._state_manager.update_balance(
                exchange,
                asset,
                total_amount,
            )

        return {
            "exchange": exchange,
            "balances": balances,
        }
