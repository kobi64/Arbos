"""
ArbOS™
EX-093
Atomic Multi-Leg Paper Execution Simulator
"""


class AtomicMultiLegPaperExecution:
    def execute(self, route, atomic_snapshot, starting_value):
        if route is None:
            raise ValueError("route is required")

        if atomic_snapshot is None:
            raise ValueError("atomic_snapshot is required")

        if starting_value <= 0:
            raise ValueError("starting_value must be positive")

        route_id = str(route.get("route_id", "")).strip()
        legs = route.get("legs") or []
        snapshots = atomic_snapshot.get("snapshots") or []

        if not legs:
            raise ValueError("legs are required")

        if len(legs) != len(snapshots):
            raise ValueError("snapshot count mismatch")

        amount = float(starting_value)
        executed_legs = []

        for index, (leg, snapshot) in enumerate(
            zip(legs, snapshots),
            start=1,
        ):
            symbol = str(leg.get("symbol", "")).strip()
            snapshot_symbol = str(snapshot.get("symbol", "")).strip()

            if symbol != snapshot_symbol:
                raise ValueError("snapshot symbol mismatch")

            side = str(leg.get("side", "")).strip().lower()

            if side == "buy":
                asks = snapshot.get("asks") or []
                if not asks:
                    raise ValueError("order book unavailable")
                price = float(asks[0][0])
                output_amount = amount / price
            elif side == "sell":
                bids = snapshot.get("bids") or []
                if not bids:
                    raise ValueError("order book unavailable")
                price = float(bids[0][0])
                output_amount = amount * price
            else:
                raise ValueError("invalid side")

            executed_legs.append({
                "leg_number": index,
                "symbol": symbol,
                "side": side,
                "input_amount": amount,
                "average_price": price,
                "output_amount": output_amount,
                "atomic_snapshot": True,
            })

            amount = output_amount

        return {
            "route_id": route_id,
            "status": "COMPLETED",
            "starting_value": float(starting_value),
            "final_value": amount,
            "legs": executed_legs,
            "atomic_snapshot": True,
        }
