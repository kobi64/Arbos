"""
ArbOS™
EX-007
Transfer Feasibility

Determines whether a specific transfer amount can be executed
on a selected blockchain network after minimum-withdrawal rules,
withdrawal fees, maintenance status, and withdrawal availability.
"""

from dataclasses import dataclass
import math
from typing import Optional

from exchanges.network_registry import NetworkInfo


@dataclass
class TransferFeasibilityResult:
    feasible: bool
    net_amount: Optional[float] = None
    reason: str = ""


class TransferFeasibility:

    @staticmethod
    def evaluate(
        amount: float,
        network: NetworkInfo,
    ) -> TransferFeasibilityResult:

        if network.maintenance:
            return TransferFeasibilityResult(
                feasible=False,
                reason="network_in_maintenance",
            )

        if not network.withdraw_enabled:
            return TransferFeasibilityResult(
                feasible=False,
                reason="withdrawals_disabled",
            )

        if isinstance(amount, bool):
            return TransferFeasibilityResult(
                feasible=False,
                reason="invalid_amount",
            )

        try:
            amount = float(amount)
        except (TypeError, ValueError, OverflowError):
            return TransferFeasibilityResult(
                feasible=False,
                reason="invalid_amount",
            )

        if not math.isfinite(amount) or amount <= 0:
            return TransferFeasibilityResult(
                feasible=False,
                reason="invalid_amount",
            )

        if network.min_withdraw is None:
            return TransferFeasibilityResult(
                feasible=False,
                reason="minimum_withdrawal_unknown",
            )

        min_withdraw = network.min_withdraw

        if isinstance(min_withdraw, bool):
            return TransferFeasibilityResult(
                feasible=False,
                reason="invalid_minimum_withdrawal",
            )

        try:
            min_withdraw = float(min_withdraw)
        except (TypeError, ValueError, OverflowError):
            return TransferFeasibilityResult(
                feasible=False,
                reason="invalid_minimum_withdrawal",
            )

        if (
            not math.isfinite(min_withdraw)
            or min_withdraw < 0
        ):
            return TransferFeasibilityResult(
                feasible=False,
                reason="invalid_minimum_withdrawal",
            )

        if amount < min_withdraw:
            return TransferFeasibilityResult(
                feasible=False,
                reason="below_minimum_withdrawal",
            )

        if network.withdraw_fee is None:
            return TransferFeasibilityResult(
                feasible=False,
                reason="withdrawal_fee_unknown",
            )

        withdraw_fee = network.withdraw_fee

        if isinstance(withdraw_fee, bool):
            return TransferFeasibilityResult(
                feasible=False,
                reason="invalid_withdrawal_fee",
            )

        try:
            withdraw_fee = float(withdraw_fee)
        except (TypeError, ValueError, OverflowError):
            return TransferFeasibilityResult(
                feasible=False,
                reason="invalid_withdrawal_fee",
            )

        if (
            not math.isfinite(withdraw_fee)
            or withdraw_fee < 0
        ):
            return TransferFeasibilityResult(
                feasible=False,
                reason="invalid_withdrawal_fee",
            )

        net_amount = amount - withdraw_fee

        if net_amount <= 0:
            return TransferFeasibilityResult(
                feasible=False,
                net_amount=0.0,
                reason="withdrawal_fee_consumes_amount",
            )

        return TransferFeasibilityResult(
            feasible=True,
            net_amount=net_amount,
            reason="ok",
        )
