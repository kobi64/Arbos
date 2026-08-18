"""
ArbOS™

EX-349
Repeat / Scale Market Provenance

Captures an independent atomic market snapshot after a completed
paper execution and derives the market inputs used for repeat/scale
revalidation.

This component does not submit live orders.

EX-349 guarantees:
- a new market capture independent from execution capture
- route/symbol continuity
- atomic snapshot timing consistency
- market inputs derived from order-book depth
- caller-supplied market values are not authoritative

EX-350 extends these guarantees with:
- wall-clock snapshot-age verification
- future-dated snapshot rejection
- epoch-second / epoch-millisecond timestamp normalization
- entry-venue identity binding for repeat/scale revalidation
"""

import math

from exchanges.multi_leg_atomic_market_snapshot import (
    MultiLegAtomicMarketSnapshot,
)
from exchanges.order_book_liquidity_slippage_engine import (
    OrderBookLiquiditySlippageEngine,
)
from core.market_data_freshness_guard import (
    MarketDataFreshnessGuard,
)


class RepeatScaleMarketProvenance:
    def __init__(
        self,
        snapshot_engine,
        max_snapshot_spread_ms=250,
        max_snapshot_age_seconds=5.0,
        clock=None,
    ):
        if snapshot_engine is None:
            raise ValueError(
                "snapshot_engine is required"
            )

        self._atomic = (
            MultiLegAtomicMarketSnapshot(
                snapshot_engine,
                max_spread_ms=(
                    max_snapshot_spread_ms
                ),
            )
        )

        self._depth = (
            OrderBookLiquiditySlippageEngine()
        )

        self._freshness = (
            MarketDataFreshnessGuard(
                max_age_seconds=(
                    max_snapshot_age_seconds
                ),
                clock=clock,
            )
        )

    def capture(
        self,
        route,
        trade_amount,
        expected_entry_exchange=None,
    ):
        if not isinstance(route, dict):
            raise ValueError(
                "route is required"
            )

        route_id = str(
            route.get(
                "route_id",
                "",
            )
            or ""
        ).strip()

        if not route_id:
            raise ValueError(
                "route_id is required"
            )

        legs = route.get("legs") or []

        if not legs:
            raise ValueError(
                "route legs are required"
            )

        if isinstance(trade_amount, bool):
            raise ValueError(
                "trade_amount must be positive"
            )

        try:
            trade_amount = float(
                trade_amount
            )
        except (
            TypeError,
            ValueError,
            OverflowError,
        ):
            raise ValueError(
                "trade_amount must be positive"
            )

        if (
            not math.isfinite(trade_amount)
            or trade_amount <= 0
        ):
            raise ValueError(
                "trade_amount must be positive"
            )

        try:
            atomic = self._atomic.capture(
                route
            )
        except (
            TypeError,
            ValueError,
            KeyError,
            IndexError,
        ) as exc:
            raise ValueError(
                "fresh market snapshot required"
            ) from exc

        if (
            str(
                atomic.get(
                    "route_id",
                    "",
                )
                or ""
            ).strip()
            != route_id
        ):
            raise ValueError(
                "snapshot route_id mismatch"
            )

        snapshots = (
            atomic.get("snapshots")
            or []
        )

        if len(snapshots) != len(legs):
            raise ValueError(
                "snapshot count mismatch"
            )

        symbols = []
        exchange_ids = []

        for leg, snapshot in zip(
            legs,
            snapshots,
        ):
            if not isinstance(leg, dict):
                raise ValueError(
                    "invalid route leg"
                )

            if not isinstance(
                snapshot,
                dict,
            ):
                raise ValueError(
                    "fresh market snapshot required"
                )

            symbol = str(
                leg.get(
                    "symbol",
                    "",
                )
                or ""
            ).strip().upper()

            if not symbol:
                raise ValueError(
                    "route leg symbol is required"
                )

            snapshot_symbol = str(
                snapshot.get(
                    "symbol",
                    "",
                )
                or ""
            ).strip().upper()

            if snapshot_symbol != symbol:
                raise ValueError(
                    "snapshot symbol mismatch"
                )

            if not (
                snapshot.get("bids")
                or []
            ):
                raise ValueError(
                    "fresh order book unavailable"
                )

            if not (
                snapshot.get("asks")
                or []
            ):
                raise ValueError(
                    "fresh order book unavailable"
                )

            timestamp = snapshot.get(
                "timestamp"
            )

            if timestamp is None:
                raise ValueError(
                    "snapshot timestamp required"
                )

            try:
                timestamp = float(
                    timestamp
                )
            except (
                TypeError,
                ValueError,
                OverflowError,
            ):
                raise ValueError(
                    "invalid snapshot timestamp"
                )

            if not math.isfinite(timestamp):
                raise ValueError(
                    "invalid snapshot timestamp"
                )

            # ArbOS market timestamps use epoch seconds at
            # the freshness boundary. CCXT/native feeds may
            # supply epoch milliseconds, so normalize them.
            timestamp_seconds = timestamp

            if timestamp_seconds > 100000000000.0:
                timestamp_seconds = (
                    timestamp_seconds / 1000.0
                )

            freshness = self._freshness.evaluate(
                symbol=symbol,
                timestamp=timestamp_seconds,
            )

            if freshness.get("fresh") is not True:
                raise ValueError(
                    "fresh market snapshot required"
                )

            symbols.append(symbol)

            exchange_id = str(
                snapshot.get(
                    "exchange_id",
                    "",
                )
                or ""
            ).strip().lower()

            if exchange_id:
                exchange_ids.append(
                    exchange_id
                )

        entry_leg = legs[0]
        entry_snapshot = snapshots[0]

        expected_entry_exchange = str(
            expected_entry_exchange
            or route.get(
                "source_exchange",
                "",
            )
            or ""
        ).strip().lower()

        captured_entry_exchange = str(
            entry_snapshot.get(
                "exchange_id",
                "",
            )
            or ""
        ).strip().lower()

        if expected_entry_exchange:
            if not captured_entry_exchange:
                raise ValueError(
                    "snapshot exchange_id required"
                )

            if (
                captured_entry_exchange
                != expected_entry_exchange
            ):
                raise ValueError(
                    "snapshot exchange mismatch"
                )

        entry_side = str(
            entry_leg.get(
                "side",
                "",
            )
            or ""
        ).strip().lower()

        if entry_side not in {
            "buy",
            "sell",
        }:
            raise ValueError(
                "invalid entry side"
            )

        levels = (
            entry_snapshot["asks"]
            if entry_side == "buy"
            else entry_snapshot["bids"]
        )

        available_liquidity = 0.0

        for level in levels:
            try:
                price = float(level[0])
                quantity = float(level[1])
            except (
                TypeError,
                ValueError,
                IndexError,
                OverflowError,
            ):
                raise ValueError(
                    "invalid fresh order book level"
                )

            if (
                not math.isfinite(price)
                or not math.isfinite(quantity)
                or price <= 0
                or quantity < 0
            ):
                raise ValueError(
                    "invalid fresh order book level"
                )

            available_liquidity += (
                price * quantity
            )

        best_price = float(
            levels[0][0]
        )

        requested_quantity = (
            trade_amount / best_price
        )

        depth = self._depth.evaluate(
            side=entry_side,
            quantity=requested_quantity,
            order_book=entry_snapshot,
        )

        average_price = float(
            depth.get(
                "average_price",
                0.0,
            )
        )

        current_price = (
            average_price
            if average_price > 0
            else best_price
        )

        provenance = {
            "route_id": route_id,
            "independent_revalidation_capture": True,
            "snapshot_age_verified": True,
            "timestamp_unit": "epoch_seconds",
            "entry_exchange_expected": (
                expected_entry_exchange or None
            ),
            "entry_exchange_captured": (
                captured_entry_exchange or None
            ),
            "entry_exchange_verified": bool(
                expected_entry_exchange
                and captured_entry_exchange
                == expected_entry_exchange
            ),
            "snapshot_count": len(
                snapshots
            ),
            "symbols": list(
                symbols
            ),
            "exchange_ids": list(
                dict.fromkeys(
                    exchange_ids
                )
            ),
            "earliest_timestamp": (
                atomic[
                    "earliest_timestamp"
                ]
            ),
            "latest_timestamp": (
                atomic[
                    "latest_timestamp"
                ]
            ),
            "snapshot_spread_ms": (
                atomic[
                    "snapshot_spread_ms"
                ]
            ),
            "entry_symbol": symbols[0],
            "entry_side": entry_side,
            "available_liquidity": (
                available_liquidity
            ),
            "best_price": best_price,
            "average_price": (
                current_price
            ),
            "slippage_percent": float(
                depth.get(
                    "slippage_percent",
                    0.0,
                )
            ),
            "depth_filled": (
                depth.get("filled")
                is True
            ),
            "market_inputs_derived_from_snapshot": True,
            "caller_market_values_authoritative": False,
            "paper_only": True,
            "live_order_submitted": False,
        }

        return {
            "available_liquidity": (
                available_liquidity
            ),
            "expected_price": best_price,
            "current_price": current_price,
            "market_provenance": provenance,
        }
