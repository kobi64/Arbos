"""
ArbOS™
EX-129
Withdrawal-Aware Bridge Conversion Planner
"""

from exchanges.transfer_feasibility import (
    TransferFeasibility,
)


class WithdrawalAwareBridgeConversionPlanner:
    def plan(
        self,
        coin,
        amount,
        coin_network,
        btc_network,
        spot_conversion_available,
        convert_quote_available,
    ):
        direct = TransferFeasibility.evaluate(
            amount=amount,
            network=coin_network,
        )

        if direct.feasible:
            return {
                "coin": str(coin).strip().upper(),
                "route_type": "DIRECT_WITHDRAWAL",
                "bridge_asset": None,
                "conversion_required": False,
                "conversion_method": None,
                "reason": "direct_withdrawal_available",
            }

        if spot_conversion_available:
            return {
                "coin": str(coin).strip().upper(),
                "route_type": "SPOT_BRIDGE_CONVERSION",
                "bridge_asset": "BTC",
                "conversion_required": True,
                "conversion_method": "spot",
                "reason": "coin_withdrawal_unavailable",
            }

        if convert_quote_available:
            return {
                "coin": str(coin).strip().upper(),
                "route_type": "CONVERT_SWAP_BRIDGE",
                "bridge_asset": "BTC",
                "conversion_required": True,
                "conversion_method": "convert_swap",
                "reason": "coin_withdrawal_unavailable",
            }

        return {
            "coin": str(coin).strip().upper(),
            "route_type": "REJECTED",
            "bridge_asset": None,
            "conversion_required": False,
            "conversion_method": None,
            "reason": "no_transfer_or_conversion_path",
        }
