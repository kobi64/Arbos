"""
ArbOS™
EX-081
Safe Live Paper Readiness Gate
"""

from exchanges.execution_readiness_validation import (
    ExecutionReadinessValidation,
)
from exchanges.pre_execution_validation import (
    PreExecutionValidationPipeline,
)


class SafeLivePaperReadinessGate:
    def __init__(self):
        self._order_validator = PreExecutionValidationPipeline()
        self._history = []

    def evaluate(
        self,
        opportunity,
        exchange_connected,
        account_valid,
        trading_pair_active,
        sufficient_balance,
        gas_available,
        withdrawal_enabled,
        approval_granted,
    ):
        if opportunity is None:
            raise ValueError("opportunity is required")

        if not isinstance(approval_granted, bool):
            raise ValueError("approval_granted must be boolean")

        legs = opportunity.get("legs")

        if not legs:
            raise ValueError("legs are required")

        for index, leg in enumerate(legs, start=1):
            order = {
                "symbol": leg.get("symbol"),
                "side": leg.get("side"),
                "order_type": leg.get("order_type", "market"),
                "quantity": leg.get("quantity"),
                "price": leg.get("price"),
            }

            validation = self._order_validator.validate(order)

            if not validation["valid"]:
                result = {
                    "ready": False,
                    "reason": "order_validation_failed",
                    "leg_number": index,
                    "validation_reasons": validation["reasons"],
                }
                self._history.append(dict(result))
                return dict(result)

        readiness = ExecutionReadinessValidation.validate(
            exchange_connected=exchange_connected,
            account_valid=account_valid,
            trading_pair_active=trading_pair_active,
            sufficient_balance=sufficient_balance,
            gas_available=gas_available,
            withdrawal_enabled=withdrawal_enabled,
        )

        if not readiness["ready"]:
            result = {
                "ready": False,
                "reason": readiness["reason"],
            }
            self._history.append(dict(result))
            return dict(result)

        if not approval_granted:
            result = {
                "ready": False,
                "reason": "approval_required",
            }
            self._history.append(dict(result))
            return dict(result)

        result = {
            "ready": True,
            "reason": "ready_for_safe_live_paper_execution",
        }

        self._history.append(dict(result))
        return dict(result)

    def history(self):
        return [dict(record) for record in self._history]
