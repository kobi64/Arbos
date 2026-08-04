"""
ArbOS™
EX-092
Multi-Leg Atomic Market Snapshot Coordinator
"""


class MultiLegAtomicMarketSnapshot:
    def __init__(self, snapshot_engine, max_spread_ms=250):
        self._snapshot_engine = snapshot_engine
        self._max_spread_ms = float(max_spread_ms)

    def capture(self, route, limit=None):
        if route is None:
            raise ValueError("route is required")

        legs = route.get("legs")
        if not legs:
            raise ValueError("legs are required")

        snapshots = []

        for leg in legs:
            symbol = leg.get("symbol")
            snapshot = self._snapshot_engine.snapshot(
                symbol,
                limit=limit,
            )
            snapshots.append(snapshot)

        timestamps = [
            snapshot.get("timestamp")
            for snapshot in snapshots
            if snapshot.get("timestamp") is not None
        ]

        earliest_timestamp = min(timestamps)
        latest_timestamp = max(timestamps)
        snapshot_spread_ms = latest_timestamp - earliest_timestamp

        if snapshot_spread_ms > self._max_spread_ms:
            raise ValueError("snapshot spread exceeded")

        return {
            "route_id": str(route.get("route_id", "")).strip(),
            "snapshots": snapshots,
            "earliest_timestamp": earliest_timestamp,
            "latest_timestamp": latest_timestamp,
            "snapshot_spread_ms": snapshot_spread_ms,
        }
