"""
ArbOS™
EX-003
Network Registry

Maintains blockchain network information for supported assets.
"""

from dataclasses import dataclass
from typing import Dict, List


@dataclass
class NetworkInfo:
    coin: str
    network: str

    deposit_enabled: bool = True
    withdraw_enabled: bool = True

    maintenance: bool = False

    withdraw_fee: float = 0.0
    min_withdraw: float = 0.0

    confirmations: int = 0


class NetworkRegistry:

    def __init__(self):
        self.networks: Dict[str, List[NetworkInfo]] = {}

    def add_network(self, info: NetworkInfo) -> None:
        coin = info.coin.upper()

        if coin not in self.networks:
            self.networks[coin] = []

        self.networks[coin].append(info)

    def get_networks(self, coin: str) -> List[NetworkInfo]:
        return self.networks.get(coin.upper(), [])

    def executable_networks(self, coin: str) -> List[NetworkInfo]:
        return [
            network
            for network in self.get_networks(coin)
            if (
                network.deposit_enabled
                and network.withdraw_enabled
                and not network.maintenance
            )
        ]
