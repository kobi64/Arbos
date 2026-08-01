"""
ArbOS™
EX-006
Route Validator

Validates whether a transfer route between two exchanges
is executable and selects the lowest-fee compatible network.
"""

from dataclasses import dataclass
from typing import List, Optional

from exchanges.network_compatibility import NetworkCompatibility
from exchanges.network_registry import NetworkInfo


@dataclass
class RouteValidationResult:
    executable: bool
    network: Optional[str] = None
    withdraw_fee: float = 0.0


class RouteValidator:

    @staticmethod
    def validate_transfer_route(
        source_networks: List[NetworkInfo],
        destination_networks: List[NetworkInfo],
    ) -> RouteValidationResult:

        compatible = NetworkCompatibility.compatible_networks(
            source_networks,
            destination_networks,
        )

        if not compatible:
            return RouteValidationResult(
                executable=False,
                network=None,
                withdraw_fee=0.0,
            )

        best_network = min(
            compatible,
            key=lambda network: network.withdraw_fee,
        )

        return RouteValidationResult(
            executable=True,
            network=best_network.network,
            withdraw_fee=best_network.withdraw_fee,
        )
