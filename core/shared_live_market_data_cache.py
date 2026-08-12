"""
ArbOS™
EX-201
Shared Live Market Data Cache

Stores the latest public market snapshot per exchange/symbol.

Newer sequence updates replace older state.
Older and duplicate sequence updates are rejected.
Reads are deep-copy safe.

Optional freshness evaluation delegates to the existing
MarketDataFreshnessGuard contract.

Paper/public-data infrastructure only.
No authentication.
No transfers.
No live orders.
"""

from copy import deepcopy


class SharedLiveMarketDataCache:
    def __init__(
        self,
        freshness_guard=None,
    ):
        self._freshness_guard = (
            freshness_guard
        )
        self._markets = {}

    def update(
        self,
        snapshot,
    ):
        if snapshot is None:
            raise ValueError(
                "snapshot is required"
            )

        exchange_id = str(
            snapshot.get(
                "exchange_id",
                "",
            )
            or ""
        ).strip().lower()

        if not exchange_id:
            raise ValueError(
                "exchange_id is required"
            )

        symbol = str(
            snapshot.get(
                "symbol",
                "",
            )
            or ""
        ).strip().upper()

        if not symbol:
            raise ValueError(
                "symbol is required"
            )

        if snapshot.get(
            "timestamp"
        ) is None:
            raise ValueError(
                "timestamp is required"
            )

        key = (
            exchange_id,
            symbol,
        )

        incoming_sequence = snapshot.get(
            "sequence"
        )

        existing = self._markets.get(
            key
        )

        if existing is not None:
            existing_sequence = (
                existing.get(
                    "sequence"
                )
            )

            if (
                incoming_sequence is not None
                and existing_sequence is not None
            ):
                if (
                    incoming_sequence
                    < existing_sequence
                ):
                    return {
                        "updated": False,
                        "reason": (
                            "stale_market_sequence"
                        ),
                        "exchange_id": (
                            exchange_id
                        ),
                        "symbol": symbol,
                    }

                if (
                    incoming_sequence
                    == existing_sequence
                ):
                    return {
                        "updated": False,
                        "reason": (
                            "duplicate_market_sequence"
                        ),
                        "exchange_id": (
                            exchange_id
                        ),
                        "symbol": symbol,
                    }

        record = deepcopy(
            snapshot
        )

        record[
            "exchange_id"
        ] = exchange_id

        record[
            "symbol"
        ] = symbol

        self._markets[
            key
        ] = record

        return {
            "updated": True,
            "reason": None,
            "exchange_id": (
                exchange_id
            ),
            "symbol": symbol,
            "sequence": (
                incoming_sequence
            ),
            "paper_only": True,
            "live_order_submitted": False,
        }

    def get(
        self,
        exchange_id,
        symbol,
    ):
        key = self._normalize_key(
            exchange_id=exchange_id,
            symbol=symbol,
        )

        snapshot = self._markets.get(
            key
        )

        if snapshot is None:
            return None

        return deepcopy(
            snapshot
        )

    def get_with_freshness(
        self,
        exchange_id,
        symbol,
    ):
        snapshot = self.get(
            exchange_id=exchange_id,
            symbol=symbol,
        )

        if snapshot is None:
            return {
                "snapshot": None,
                "freshness": None,
                "paper_only": True,
                "live_order_submitted": False,
            }

        freshness = None

        if (
            self._freshness_guard
            is not None
        ):
            freshness = (
                self._freshness_guard.evaluate(
                    symbol=snapshot[
                        "symbol"
                    ],
                    timestamp=snapshot[
                        "timestamp"
                    ],
                )
            )

        return {
            "snapshot": snapshot,
            "freshness": (
                deepcopy(
                    freshness
                )
                if freshness is not None
                else None
            ),
            "paper_only": True,
            "live_order_submitted": False,
        }

    def market_count(
        self,
    ):
        return len(
            self._markets
        )

    @staticmethod
    def _normalize_key(
        exchange_id,
        symbol,
    ):
        exchange_id = str(
            exchange_id
            or ""
        ).strip().lower()

        symbol = str(
            symbol
            or ""
        ).strip().upper()

        if not exchange_id:
            raise ValueError(
                "exchange_id is required"
            )

        if not symbol:
            raise ValueError(
                "symbol is required"
            )

        return (
            exchange_id,
            symbol,
        )
