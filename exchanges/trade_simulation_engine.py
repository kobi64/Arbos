"""
ArbOS™
EX-040
Trade Simulation Engine

Provides a risk-free environment for testing
arbitrage execution before real capital deployment.
"""

from datetime import datetime, UTC


class TradeSimulationEngine:

    def __init__(self):
        self._balances = {}
        self._history = [
            {
                "action": "simulation_engine_created",
                "timestamp": datetime.now(UTC).isoformat(),
            }
        ]

    def create_balance(self, asset, amount):

        balance = {
            "asset": asset,
            "amount": amount,
        }

        self._balances[asset] = amount

        self._history.append(
            {
                "action": "balance_created",
                **balance,
                "timestamp": datetime.now(UTC).isoformat(),
            }
        )

        return balance

    def simulate_trade(
        self,
        input_asset,
        output_asset,
        amount,
        expected_return,
        fees,
        slippage,
    ):

        final_return = round(
            expected_return
            - fees
            - slippage,
            2,
        )

        profit = round(
            final_return - amount,
            2,
        )

        result = {
            "input_asset": input_asset,
            "output_asset": output_asset,
            "amount": amount,
            "expected_return": expected_return,
            "fees": fees,
            "slippage": slippage,
            "final_return": final_return,
            "profit": profit,
            "success": profit > 0,
        }

        self._history.append(
            {
                "action": "trade_simulated",
                **result,
                "timestamp": datetime.now(UTC).isoformat(),
            }
        )

        return result

    def get_history(self):
        return self._history
