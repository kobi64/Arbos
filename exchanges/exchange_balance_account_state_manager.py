"""
ArbOS™
EX-053
Exchange Balance & Account State Manager

Maintains exchange balances and account state
for execution validation.
"""


class ExchangeBalanceAccountStateManager:

    def __init__(self):

        self._balances = {}
        self._status = {}

    def update_balance(
        self,
        exchange,
        asset,
        amount
    ):

        if exchange not in self._balances:

            self._balances[exchange] = {}

        self._balances[exchange][asset] = amount

        return {
            "success": True,
            "exchange": exchange,
            "asset": asset,
            "amount": amount,
        }

    def get_balance(
        self,
        exchange,
        asset
    ):

        return self._balances.get(
            exchange,
            {}
        ).get(
            asset
        )

    def validate_funds(
        self,
        exchange,
        asset,
        required_amount
    ):

        balance = self.get_balance(
            exchange,
            asset
        )

        if balance is None:
            return False

        return balance >= required_amount

    def set_account_status(
        self,
        exchange,
        status
    ):

        self._status[exchange] = status

        return {
            "exchange": exchange,
            "status": status,
        }

    def get_snapshot(
        self,
        exchange
    ):

        return {
            "exchange": exchange,
            "balances": self._balances.get(
                exchange,
                {}
            ),
            "status": self._status.get(
                exchange,
                "UNKNOWN"
            ),
        }
