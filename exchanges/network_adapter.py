"""
ArbOS™
EX-004
Exchange Network Adapter

Converts exchange-specific network dictionaries into
standardized NetworkInfo objects used by the Network Registry.
"""

from typing import Dict, List

from exchanges.network_registry import NetworkInfo


class ExchangeNetworkAdapter:

    @staticmethod
    def normalize_network(
        coin: str,
        raw: Dict
    ) -> NetworkInfo:
        return NetworkInfo(
            coin=coin,
            network=str(raw.get("network", "")).upper(),
            deposit_enabled=bool(raw.get("deposit_enabled", False)),
            withdraw_enabled=bool(raw.get("withdraw_enabled", False)),
            maintenance=bool(raw.get("maintenance", False)),
            withdraw_fee=(
                float(raw["withdraw_fee"])
                if raw.get("withdraw_fee") is not None
                else None
            ),
            min_withdraw=(
                float(raw["min_withdraw"])
                if raw.get("min_withdraw") is not None
                else None
            ),
            confirmations=(
                int(raw["confirmations"])
                if raw.get("confirmations") is not None
                else None
            ),
        )

    @classmethod
    def normalize_networks(
        cls,
        coin: str,
        raw_networks: List[Dict]
    ) -> List[NetworkInfo]:
        return [
            cls.normalize_network(coin, raw)
            for raw in raw_networks
        ]
