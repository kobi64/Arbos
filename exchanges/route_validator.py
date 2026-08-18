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
    withdraw_fee: Optional[float] = None


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
                withdraw_fee=None,
            )

        known_fee_networks = [
            network
            for network in compatible
            if network.withdraw_fee is not None
        ]

        if not known_fee_networks:
            return RouteValidationResult(
                executable=False,
                network=None,
                withdraw_fee=None,
            )

        best_network = min(
            known_fee_networks,
            key=lambda network: network.withdraw_fee,
        )

        return RouteValidationResult(
            executable=True,
            network=best_network.network,
            withdraw_fee=best_network.withdraw_fee,
        )


def _identity_verified_transfer_route(
    source_exchange,
    destination_exchange,
    coin,
    source_network_records,
    destination_network_records,
):
    """
    EX-177 strict network-identity route validation.

    Unlike the legacy EX-006 method, matching display names alone
    are not sufficient. A source/destination network pair must be
    VERIFIED by ExchangeNetworkIdentityValidator before it can be
    considered executable.
    """
    from exchanges.exchange_network_identity_validator import (
        ExchangeNetworkIdentityValidator,
    )

    if not source_network_records:
        return RouteValidationResult(
            executable=False,
            network=None,
            withdraw_fee=None,
        )

    if not destination_network_records:
        return RouteValidationResult(
            executable=False,
            network=None,
            withdraw_fee=None,
        )

    validator = ExchangeNetworkIdentityValidator()

    verified = []

    for source in source_network_records:
        source_name = str(
            source.get(
                "network_name",
                source.get(
                    "network",
                    source.get(
                        "chain_name",
                        source.get("chain", ""),
                    ),
                ),
            )
        ).strip().upper()

        if not source_name:
            continue

        for destination in destination_network_records:
            destination_name = str(
                destination.get(
                    "network_name",
                    destination.get(
                        "network",
                        destination.get(
                            "chain_name",
                            destination.get(
                                "chain",
                                "",
                            ),
                        ),
                    ),
                )
            ).strip().upper()

            if (
                not destination_name
                or source_name != destination_name
            ):
                continue

            identity = validator.validate(
                coin=coin,
                source_exchange=source_exchange,
                destination_exchange=destination_exchange,
                source_network=source,
                destination_network=destination,
            )

            if identity.get(
                "execution_allowed"
            ) is not True:
                continue

            fee = source.get(
                "withdraw_fee",
                source.get(
                    "fee",
                    None,
                ),
            )

            if fee is None:
                continue

            verified.append({
                "network": source_name,
                "withdraw_fee": float(fee),
                "identity_result": identity,
            })

    if not verified:
        return RouteValidationResult(
            executable=False,
            network=None,
            withdraw_fee=None,
        )

    best = min(
        verified,
        key=lambda item: item[
            "withdraw_fee"
        ],
    )

    return RouteValidationResult(
        executable=True,
        network=best["network"],
        withdraw_fee=best["withdraw_fee"],
    )


RouteValidator.validate_identity_verified_transfer_route = (
    staticmethod(
        _identity_verified_transfer_route
    )
)
