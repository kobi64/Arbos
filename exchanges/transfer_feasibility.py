"""
ArbOS™
EX-007
Transfer Feasibility

Determines whether a specific transfer amount can be executed
on a selected blockchain network after minimum-withdrawal rules,
withdrawal fees, maintenance status, and withdrawal availability.
"""

from dataclasses import dataclass
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

        if network.min_withdraw is None:
            return TransferFeasibilityResult(
                feasible=False,
                reason="minimum_withdrawal_unknown",
            )

        if amount < network.min_withdraw:
            return TransferFeasibilityResult(
                feasible=False,
                reason="below_minimum_withdrawal",
            )

        if network.withdraw_fee is None:
            return TransferFeasibilityResult(
                feasible=False,
                reason="withdrawal_fee_unknown",
            )

        net_amount = amount - network.withdraw_fee

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
