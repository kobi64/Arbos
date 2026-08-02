"""
ArbOS™
EX-033
Execution Position Tracker

Tracks assets, balances, locations, and position history.

Responsibilities:
- Add asset positions
- Update balances
- Track asset locations
- Compare expected vs actual holdings
- Maintain position history
"""


from datetime import datetime, UTC


class ExecutionPositionTracker:

    def __init__(self, execution_id: str):
        if not execution_id:
            raise ValueError("execution_id is required")

        self.execution_id = execution_id
        self._positions = {}

        self._history = [
            {
                "execution_id": execution_id,
                "status": "created",
                "timestamp": datetime.now(UTC).isoformat(),
            }
        ]

    def add_position(
        self,
        asset: str,
        amount: float,
        location: str,
    ):

        if not asset:
            raise ValueError("asset required")

        position = {
            "asset": asset,
            "amount": amount,
            "location": location,
        }

        self._positions[asset] = position

        self._history.append(
            {
                "execution_id": self.execution_id,
                "action": "add",
                **position,
                "timestamp": datetime.now(UTC).isoformat(),
            }
        )

        return position

    def update_position(
        self,
        asset: str,
        amount: float,
        location: str,
    ):

        if not asset:
            raise ValueError("asset required")

        position = {
            "asset": asset,
            "amount": amount,
            "location": location,
        }

        self._positions[asset] = position

        self._history.append(
            {
                "execution_id": self.execution_id,
                "action": "update",
                **position,
                "timestamp": datetime.now(UTC).isoformat(),
            }
        )

        return position

    def get_position(self, asset: str):

        if asset not in self._positions:
            raise ValueError("asset not found")

        return self._positions[asset]

    def compare_position(
        self,
        asset: str,
        expected_amount: float,
    ):

        position = self.get_position(asset)

        if position["amount"] == expected_amount:
            return {
                "asset": asset,
                "status": "matched",
            }

        return {
            "asset": asset,
            "status": "mismatch",
            "expected": expected_amount,
            "actual": position["amount"],
        }

    def get_history(self):
        return self._history
