"""
ArbOS™
EX-005
Network Compatibility

Finds blockchain networks that are executable between
a source exchange and a destination exchange.
"""

from typing import List

from exchanges.network_registry import NetworkInfo


class NetworkCompatibility:

    @staticmethod
    def compatible_networks(
        source_networks: List[NetworkInfo],
        destination_networks: List[NetworkInfo],
    ) -> List[NetworkInfo]:

        destination_map = {
            network.network.upper(): network
            for network in destination_networks
            if (
                network.deposit_enabled
                and not network.maintenance
            )
        }

        compatible = []

        for source in source_networks:
            network_name = source.network.upper()

            if (
                source.withdraw_enabled
                and not source.maintenance
                and network_name in destination_map
            ):
                compatible.append(source)

        return compatible
