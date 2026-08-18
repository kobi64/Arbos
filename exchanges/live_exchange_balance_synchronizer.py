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
            free_value = free.get(asset)
            used_value = used.get(asset)
            total_value = total.get(asset)

            free_amount = (
                float(free_value)
                if free_value is not None
                else None
            )
            used_amount = (
                float(used_value)
                if used_value is not None
                else None
            )
            total_amount = (
                float(total_value)
                if total_value is not None
                else None
            )

            balances[asset] = {
                "free": free_amount,
                "used": used_amount,
                "total": total_amount,
            }

            if total_amount is not None:
                self._state_manager.update_balance(
                    exchange,
                    asset,
                    total_amount,
                )

        return {
            "exchange": exchange,
            "balances": balances,
        }
