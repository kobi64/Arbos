"""
ArbOS™
EX-010
Transfer Route Cost

Combines transfer-route feasibility with transfer-cost analysis
to select the lowest-cost executable route that remains within
the configured maximum transfer-cost threshold.
"""

from dataclasses import dataclass
from typing import List, Optional

from exchanges.network_compatibility import NetworkCompatibility
from exchanges.network_registry import NetworkInfo
from exchanges.transfer_cost_analysis import TransferCostAnalysis
from exchanges.transfer_feasibility import TransferFeasibility


@dataclass
class TransferRouteCostResult:
    executable: bool
    network: Optional[str] = None
    withdraw_fee: Optional[float] = None
    cost_percent: float = 0.0
    net_amount: float = 0.0
    reason: str = ""


class TransferRouteCost:

    @staticmethod
    def evaluate(
        amount: float,
        source_networks: List[NetworkInfo],
        destination_networks: List[NetworkInfo],
        max_cost_percent: float,
    ) -> TransferRouteCostResult:

        if amount <= 0:
            return TransferRouteCostResult(
                executable=False,
                reason="invalid_amount",
            )

        compatible = NetworkCompatibility.compatible_networks(
            source_networks,
            destination_networks,
        )

        if not compatible:
            return TransferRouteCostResult(
                executable=False,
                reason="no_compatible_network",
            )

        acceptable_routes = []

        for network in compatible:
            feasibility = TransferFeasibility.evaluate(
                amount=amount,
                network=network,
            )

            if not feasibility.feasible:
                continue

            cost = TransferCostAnalysis.evaluate(
                amount=amount,
                network=network,
                max_cost_percent=max_cost_percent,
            )

            if cost.acceptable:
                acceptable_routes.append(
                    (network, cost)
                )

        if not acceptable_routes:
            return TransferRouteCostResult(
                executable=False,
                reason="no_economically_acceptable_route",
            )

        best_network, best_cost = min(
            acceptable_routes,
            key=lambda route: route[0].withdraw_fee,
        )

        return TransferRouteCostResult(
            executable=True,
            network=best_network.network,
            withdraw_fee=best_cost.withdraw_fee,
            cost_percent=best_cost.cost_percent,
            net_amount=best_cost.net_amount,
            reason="ok",
        )
