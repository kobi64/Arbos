"""
ArbOS™
EX-207
Live Feed Subscription Batch Planner

Normalizes, deduplicates, prioritizes, and batches
live-market symbols within configured subscription limits.

Planning only.
No authentication.
No transfers.
No live orders.
"""


class LiveFeedSubscriptionBatchPlanner:
    def __init__(
        self,
        max_symbols_per_batch,
        max_batches,
    ):
        if max_symbols_per_batch <= 0:
            raise ValueError(
                "max_symbols_per_batch must be positive"
            )

        if max_batches <= 0:
            raise ValueError(
                "max_batches must be positive"
            )

        self._max_symbols_per_batch = int(
            max_symbols_per_batch
        )
        self._max_batches = int(
            max_batches
        )

    def plan(
        self,
        exchange_id,
        symbols,
    ):
        if (
            exchange_id is None
            or not str(exchange_id).strip()
        ):
            raise ValueError(
                "exchange_id is required"
            )

        if not symbols:
            raise ValueError(
                "symbols are required"
            )

        exchange_id = (
            str(exchange_id)
            .strip()
            .lower()
        )

        normalized = []
        seen = set()

        for symbol in symbols:
            if symbol is None:
                continue

            symbol = (
                str(symbol)
                .strip()
                .upper()
            )

            if not symbol:
                continue

            if symbol in seen:
                continue

            seen.add(symbol)
            normalized.append(symbol)

        if not normalized:
            raise ValueError(
                "symbols are required"
            )

        capacity = (
            self._max_symbols_per_batch
            * self._max_batches
        )

        selected_symbols = normalized[
            :capacity
        ]
        overflow_symbols = normalized[
            capacity:
        ]

        batches = []

        for index in range(
            0,
            len(selected_symbols),
            self._max_symbols_per_batch,
        ):
            batches.append(
                selected_symbols[
                    index:
                    index
                    + self._max_symbols_per_batch
                ]
            )

        return {
            "exchange_id": exchange_id,
            "batches": batches,
            "batch_count": len(batches),
            "selected_symbols": (
                selected_symbols
            ),
            "selected_symbol_count": len(
                selected_symbols
            ),
            "overflow_symbols": (
                overflow_symbols
            ),
            "overflow_symbol_count": len(
                overflow_symbols
            ),
            "max_symbols_per_batch": (
                self._max_symbols_per_batch
            ),
            "max_batches": (
                self._max_batches
            ),
            "capacity": capacity,
            "paper_only": True,
            "live_order_submitted": False,
        }
