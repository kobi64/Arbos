"""
ArbOS™
EX-203
Shared Cache Route Worker

Consumes coalesced route work and evaluates registered
multi-leg routes using only shared cached market snapshots.

No exchange API request is made during route evaluation.

The worker reuses the existing
OrderBookDepthAwareTriangleScanner for depth, liquidity,
slippage, fee, and P&L calculations.

Paper/public-data infrastructure only.
No authentication.
No transfers.
No live orders.
"""

from copy import deepcopy

from core.order_book_depth_aware_triangle_scanner import (
    OrderBookDepthAwareTriangleScanner,
)


class _SharedCacheOrderBookProvider:
    def __init__(
        self,
        market_cache,
        exchange_id,
    ):
        self._market_cache = (
            market_cache
        )

        self._exchange_id = str(
            exchange_id
            or ""
        ).strip().lower()

        self._validated = {}

    def preload(
        self,
        symbols,
    ):
        for symbol in symbols:
            normalized_symbol = str(
                symbol
                or ""
            ).strip().upper()

            result = (
                self._market_cache
                .get_with_freshness(
                    exchange_id=(
                        self._exchange_id
                    ),
                    symbol=(
                        normalized_symbol
                    ),
                )
            )

            snapshot = result.get(
                "snapshot"
            )

            if snapshot is None:
                return {
                    "ready": False,
                    "reason": (
                        "market_snapshot_unavailable"
                    ),
                    "symbol": (
                        normalized_symbol
                    ),
                }

            freshness = result.get(
                "freshness"
            )

            if (
                freshness is not None
                and freshness.get(
                    "fresh"
                )
                is False
            ):
                return {
                    "ready": False,
                    "reason": freshness.get(
                        "reason",
                        "market_data_stale",
                    ),
                    "symbol": (
                        normalized_symbol
                    ),
                }

            self._validated[
                normalized_symbol
            ] = deepcopy(
                snapshot
            )

        return {
            "ready": True,
        }

    def snapshot(
        self,
        symbol,
    ):
        normalized_symbol = str(
            symbol
            or ""
        ).strip().upper()

        snapshot = self._validated.get(
            normalized_symbol
        )

        if snapshot is None:
            raise ValueError(
                "market snapshot unavailable"
            )

        return deepcopy(
            snapshot
        )


class SharedCacheRouteWorker:
    def __init__(
        self,
        work_queue,
        market_cache,
        route_registry,
    ):
        if work_queue is None:
            raise ValueError(
                "work_queue is required"
            )

        if market_cache is None:
            raise ValueError(
                "market_cache is required"
            )

        if route_registry is None:
            raise ValueError(
                "route_registry is required"
            )

        self._work_queue = (
            work_queue
        )

        self._market_cache = (
            market_cache
        )

        self._route_registry = (
            route_registry
        )

    def process_next(
        self,
    ):
        work = (
            self._work_queue.dequeue()
        )

        if work is None:
            return None

        route_id = str(
            work.get(
                "route_id",
                "",
            )
            or ""
        ).strip()

        route = self._route_registry.get(
            route_id
        )

        if route is None:
            return {
                "processed": True,
                "route_id": route_id,
                "filled": False,
                "reason": (
                    "route_not_registered"
                ),
                "paper_only": True,
                "live_order_submitted": False,
            }

        exchange_id = str(
            route.get(
                "exchange_id",
                "",
            )
            or ""
        ).strip().lower()

        legs = (
            route.get(
                "legs"
            )
            or []
        )

        symbols = [
            str(
                leg.get(
                    "symbol",
                    "",
                )
                or ""
            ).strip().upper()
            for leg in legs
        ]

        provider = (
            _SharedCacheOrderBookProvider(
                market_cache=(
                    self._market_cache
                ),
                exchange_id=(
                    exchange_id
                ),
            )
        )

        readiness = (
            provider.preload(
                symbols
            )
        )

        if (
            readiness.get(
                "ready"
            )
            is not True
        ):
            symbol = readiness.get(
                "symbol"
            )

            reason = readiness.get(
                "reason"
            )

            result = {
                "processed": True,
                "route_id": route_id,
                "filled": False,
                "reason": reason,
                "paper_only": True,
                "live_order_submitted": False,
            }

            if (
                reason
                == "market_snapshot_unavailable"
            ):
                result[
                    "missing_symbol"
                ] = symbol

            else:
                result[
                    "stale_symbol"
                ] = symbol

            return result

        scanner = (
            OrderBookDepthAwareTriangleScanner(
                provider
            )
        )

        scan_route = {
            "route_id": (
                route_id
            ),
            "legs": deepcopy(
                legs
            ),
        }

        scanned = scanner.scan_route(
            route=scan_route,
            starting_value=float(
                route.get(
                    "starting_value"
                )
            ),
            fee_rate=float(
                route.get(
                    "fee_rate",
                    0.0,
                )
            ),
            max_slippage_percent=float(
                route.get(
                    "max_slippage_percent",
                    0.0,
                )
            ),
        )

        return {
            **scanned,
            "processed": True,
            "route_id": route_id,
            "exchange_id": (
                exchange_id
            ),
            "work_sequence": (
                work.get(
                    "sequence"
                )
            ),
            "paper_only": True,
            "live_order_submitted": False,
        }
