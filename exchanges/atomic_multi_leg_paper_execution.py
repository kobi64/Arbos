"""
ArbOS™
EX-093
Atomic Multi-Leg Paper Execution Simulator
"""

import math


class AtomicMultiLegPaperExecution:
    @staticmethod
    def _positive_finite_number(value, message):
        try:
            value = float(value)
        except (TypeError, ValueError):
            raise ValueError(message)

        if not math.isfinite(value) or value <= 0:
            raise ValueError(message)

        return value

    @classmethod
    def _top_of_book_price(cls, levels):
        if not levels:
            raise ValueError("order book unavailable")

        try:
            raw_price = levels[0][0]
        except (IndexError, TypeError, KeyError):
            raise ValueError("order book price unavailable")

        return cls._positive_finite_number(
            raw_price,
            "order book price unavailable",
        )

    def execute(self, route, atomic_snapshot, starting_value):
        if route is None:
            raise ValueError("route is required")

        if atomic_snapshot is None:
            raise ValueError("atomic_snapshot is required")

        starting_value = self._positive_finite_number(
            starting_value,
            "starting_value must be positive",
        )

        route_id = str(route.get("route_id", "")).strip()
        legs = route.get("legs") or []
        snapshots = atomic_snapshot.get("snapshots") or []

        if not legs:
            raise ValueError("legs are required")

        if len(legs) != len(snapshots):
            raise ValueError("snapshot count mismatch")

        amount = starting_value
        executed_legs = []

        for index, (leg, snapshot) in enumerate(
            zip(legs, snapshots),
            start=1,
        ):
            symbol = str(leg.get("symbol", "")).strip()
            snapshot_symbol = str(
                snapshot.get("symbol", "")
            ).strip()

            if symbol != snapshot_symbol:
                raise ValueError("snapshot symbol mismatch")

            side = str(
                leg.get("side", "")
            ).strip().lower()

            if side == "buy":
                price = self._top_of_book_price(
                    snapshot.get("asks")
                )
                output_amount = amount / price
            elif side == "sell":
                price = self._top_of_book_price(
                    snapshot.get("bids")
                )
                output_amount = amount * price
            else:
                raise ValueError("invalid side")

            if (
                not math.isfinite(output_amount)
                or output_amount <= 0
            ):
                raise ValueError(
                    "execution output amount unavailable"
                )

            output_amount = float(output_amount)

            executed_legs.append(
                {
                    "leg_number": index,
                    "symbol": symbol,
                    "side": side,
                    "input_amount": float(amount),
                    "average_price": price,
                    "output_amount": output_amount,
                    "atomic_snapshot": True,
                }
            )

            amount = output_amount

        return {
            "route_id": route_id,
            "status": "COMPLETED",
            "starting_value": starting_value,
            "final_value": float(amount),
            "legs": executed_legs,
            "atomic_snapshot": True,
        }
