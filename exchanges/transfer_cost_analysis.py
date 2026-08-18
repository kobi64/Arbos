"""
ArbOS™
EX-009
Transfer Cost Analysis

Calculates the economic cost of transferring an asset
and determines whether the withdrawal fee is acceptable
relative to the transfer amount.
"""

from dataclasses import dataclass
from typing import Optional

from exchanges.network_registry import NetworkInfo


@dataclass
class TransferCostAnalysisResult:
    acceptable: bool
    withdraw_fee: Optional[float] = None
    cost_percent: Optional[float] = None
    net_amount: Optional[float] = None
    reason: str = ""


class TransferCostAnalysis:

    @staticmethod
    def evaluate(
        amount: float,
        network: NetworkInfo,
        max_cost_percent: float,
    ) -> TransferCostAnalysisResult:

        if amount <= 0:
            return TransferCostAnalysisResult(
                acceptable=False,
                withdraw_fee=network.withdraw_fee,
                reason="invalid_amount",
            )

        if network.withdraw_fee is None:
            return TransferCostAnalysisResult(
                acceptable=False,
                withdraw_fee=None,
                reason="withdrawal_fee_unknown",
            )

        net_amount = amount - network.withdraw_fee
        cost_percent = (
            network.withdraw_fee / amount
        ) * 100

        if net_amount <= 0:
            return TransferCostAnalysisResult(
                acceptable=False,
                withdraw_fee=network.withdraw_fee,
                cost_percent=cost_percent,
                net_amount=0.0,
                reason="fee_consumes_amount",
            )

        if cost_percent > max_cost_percent:
            return TransferCostAnalysisResult(
                acceptable=False,
                withdraw_fee=network.withdraw_fee,
                cost_percent=cost_percent,
                net_amount=net_amount,
                reason="transfer_cost_too_high",
            )

        return TransferCostAnalysisResult(
            acceptable=True,
            withdraw_fee=network.withdraw_fee,
            cost_percent=cost_percent,
            net_amount=net_amount,
            reason="ok",
        )
