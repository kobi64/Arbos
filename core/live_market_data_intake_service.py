"""
ArbOS™
EX-202
Live Market Data Intake Service

Single controlled entry point for live/public market snapshots.

Flow:
snapshot
→ shared market-data cache
→ dispatch affected routes only when cache accepts update

Stale and duplicate sequence updates are rejected quietly.
Invalid snapshots still raise.

Paper/public-data infrastructure only.
No authentication.
No transfers.
No live orders.
"""


class LiveMarketDataIntakeService:
    def __init__(
        self,
        cache,
        dispatcher,
    ):
        if cache is None:
            raise ValueError(
                "cache is required"
            )

        if dispatcher is None:
            raise ValueError(
                "dispatcher is required"
            )

        self._cache = cache
        self._dispatcher = dispatcher

        self._received = 0
        self._accepted = 0
        self._rejected = 0
        self._dispatched = 0

    def submit(
        self,
        snapshot,
    ):
        self._received += 1

        try:
            cache_result = (
                self._cache.update(
                    snapshot
                )
            )
        except Exception:
            self._rejected += 1
            raise

        if (
            cache_result.get(
                "updated"
            )
            is not True
        ):
            self._rejected += 1

            return {
                **cache_result,
                "accepted": False,
                "updated": False,
                "dispatched": False,
                "paper_only": True,
                "live_order_submitted": False,
            }

        self._accepted += 1

        event = {
            "exchange_id": snapshot.get(
                "exchange_id"
            ),
            "symbol": snapshot.get(
                "symbol"
            ),
            "sequence": snapshot.get(
                "sequence"
            ),
            "priority": float(
                snapshot.get(
                    "priority",
                    0.0,
                )
                or 0.0
            ),
        }

        dispatch_result = (
            self._dispatcher.dispatch(
                event
            )
        )

        self._dispatched += 1

        return {
            **cache_result,
            "accepted": True,
            "updated": True,
            "dispatched": True,
            "dispatch": (
                dispatch_result
            ),
            "paper_only": True,
            "live_order_submitted": False,
        }

    def statistics(
        self,
    ):
        return {
            "received": (
                self._received
            ),
            "accepted": (
                self._accepted
            ),
            "rejected": (
                self._rejected
            ),
            "dispatched": (
                self._dispatched
            ),
        }
