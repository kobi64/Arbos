"""
ArbOS™
EX-021
Execution Readiness Validation

Final pre-flight check before preparing an arbitrage execution.

Validates:
- Exchange connectivity
- Account validity
- Trading pair availability
- Asset balance
- Gas/fee availability
- Withdrawal capability
"""


class ExecutionReadinessValidation:

    @staticmethod
    def validate(
        exchange_connected: bool,
        account_valid: bool,
        trading_pair_active: bool,
        sufficient_balance: bool,
        gas_available: bool,
        withdrawal_enabled: bool,
    ):
        checks = [
            exchange_connected,
            account_valid,
            trading_pair_active,
            sufficient_balance,
            gas_available,
            withdrawal_enabled,
        ]

        if not all(isinstance(value, bool) for value in checks):
            raise ValueError("all readiness checks must be boolean values")

        if not exchange_connected:
            return {
                "ready": False,
                "reason": "exchange_not_connected",
            }

        if not account_valid:
            return {
                "ready": False,
                "reason": "invalid_account",
            }

        if not trading_pair_active:
            return {
                "ready": False,
                "reason": "trading_pair_inactive",
            }

        if not sufficient_balance:
            return {
                "ready": False,
                "reason": "insufficient_balance",
            }

        if not gas_available:
            return {
                "ready": False,
                "reason": "gas_unavailable",
            }

        if not withdrawal_enabled:
            return {
                "ready": False,
                "reason": "withdrawal_disabled",
            }

        return {
            "ready": True,
            "reason": None,
        }
