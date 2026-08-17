"""
ArbOS™
EX-008
Transfer Route Evaluation

Combines network compatibility and transfer feasibility
to select the lowest-fee executable transfer route.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional

from exchanges.network_compatibility import NetworkCompatibility
from exchanges.network_registry import NetworkInfo
from exchanges.transfer_feasibility import TransferFeasibility


@dataclass
class TransferRouteEvaluationResult:
    executable: bool
    network: Optional[str] = None
    withdraw_fee: float = 0.0
    net_amount: float = 0.0
    reason: str = ""
    feasibility_diagnostics: Optional[Dict] = None


class TransferRouteEvaluation:

    @staticmethod
    def evaluate(
        amount: float,
        source_networks: List[NetworkInfo],
        destination_networks: List[NetworkInfo],
    ) -> TransferRouteEvaluationResult:

        compatible = NetworkCompatibility.compatible_networks(
            source_networks,
            destination_networks,
        )

        if not compatible:
            return TransferRouteEvaluationResult(
                executable=False,
                reason="no_compatible_network",
            )

        feasible_routes = []
        failed_routes = []

        for network in compatible:
            feasibility = TransferFeasibility.evaluate(
                amount=amount,
                network=network,
            )

            if feasibility.feasible:
                feasible_routes.append(
                    (network, feasibility)
                )
            else:
                failed_routes.append({
                    "network": network.network,
                    "reason": feasibility.reason,
                    "withdraw_fee": network.withdraw_fee,
                    "min_withdraw": network.min_withdraw,
                    "maintenance": network.maintenance,
                    "withdraw_enabled": (
                        network.withdraw_enabled
                    ),
                    "amount": amount,
                })

        if not feasible_routes:
            reasons = {}

            for failed_route in failed_routes:
                reason = failed_route["reason"]
                reasons[reason] = (
                    reasons.get(reason, 0) + 1
                )

            return TransferRouteEvaluationResult(
                executable=False,
                reason="no_feasible_network",
                feasibility_diagnostics={
                    "compatible_network_count": len(
                        compatible
                    ),
                    "failed_network_count": len(
                        failed_routes
                    ),
                    "failures_by_reason": reasons,
                    "failed_networks": failed_routes,
                },
            )

        best_network, best_feasibility = min(
            feasible_routes,
            key=lambda route: route[0].withdraw_fee,
        )

        return TransferRouteEvaluationResult(
            executable=True,
            network=best_network.network,
            withdraw_fee=best_network.withdraw_fee,
            net_amount=best_feasibility.net_amount,
            reason="ok",
        )
