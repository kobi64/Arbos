"""
ArbOS™

EX-351
Fresh Repeat / Scale Market Provenance Authorization Binding

Creates and validates a deterministic identity for the exact fresh
market provenance used by repeat/scale revalidation.

The binding is derived only from authoritative provenance fields.
It does not approve a trade, grant execution permission, or submit
an order.
"""

import hashlib
import json
import math


class RepeatScaleMarketProvenanceBinding:
    _REQUIRED_FIELDS = (
        "route_id",
        "snapshot_count",
        "symbols",
        "earliest_timestamp",
        "latest_timestamp",
        "snapshot_spread_ms",
        "entry_symbol",
        "entry_side",
        "available_liquidity",
        "best_price",
        "average_price",
        "slippage_percent",
    )

    @classmethod
    def create(cls, provenance):
        normalized = cls._normalize(
            provenance
        )

        payload = json.dumps(
            normalized,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        )

        digest = hashlib.sha256(
            payload.encode("utf-8")
        ).hexdigest()

        return {
            "market_provenance_id": (
                f"MP-{digest}"
            ),
            "market_provenance_binding": (
                normalized
            ),
        }

    @classmethod
    def verify(
        cls,
        provenance,
        market_provenance_id,
    ):
        if not isinstance(
            market_provenance_id,
            str,
        ):
            return False

        market_provenance_id = (
            market_provenance_id.strip()
        )

        if not market_provenance_id:
            return False

        try:
            expected = cls.create(
                provenance
            )["market_provenance_id"]
        except (
            TypeError,
            ValueError,
            KeyError,
        ):
            return False

        return (
            market_provenance_id
            == expected
        )

    @classmethod
    def _normalize(cls, provenance):
        if not isinstance(
            provenance,
            dict,
        ):
            raise ValueError(
                "market_provenance is required"
            )

        for field in cls._REQUIRED_FIELDS:
            if field not in provenance:
                raise ValueError(
                    f"{field} is required"
                )

        route_id = cls._required_text(
            provenance["route_id"],
            "route_id",
        )

        snapshot_count = provenance[
            "snapshot_count"
        ]

        if (
            isinstance(snapshot_count, bool)
            or not isinstance(
                snapshot_count,
                int,
            )
            or snapshot_count <= 0
        ):
            raise ValueError(
                "snapshot_count must be positive"
            )

        symbols = provenance["symbols"]

        if (
            not isinstance(symbols, list)
            or not symbols
        ):
            raise ValueError(
                "symbols are required"
            )

        normalized_symbols = []

        for symbol in symbols:
            normalized_symbols.append(
                cls._required_text(
                    symbol,
                    "symbol",
                ).upper()
            )

        exchange_ids = provenance.get(
            "exchange_ids",
            [],
        )

        if not isinstance(
            exchange_ids,
            list,
        ):
            raise ValueError(
                "exchange_ids must be a list"
            )

        normalized_exchange_ids = []

        for exchange_id in exchange_ids:
            normalized_exchange_ids.append(
                cls._required_text(
                    exchange_id,
                    "exchange_id",
                ).lower()
            )

        entry_symbol = cls._required_text(
            provenance["entry_symbol"],
            "entry_symbol",
        ).upper()

        entry_side = cls._required_text(
            provenance["entry_side"],
            "entry_side",
        ).lower()

        if entry_side not in {
            "buy",
            "sell",
        }:
            raise ValueError(
                "invalid entry_side"
            )

        numeric_fields = (
            "earliest_timestamp",
            "latest_timestamp",
            "snapshot_spread_ms",
            "available_liquidity",
            "best_price",
            "average_price",
            "slippage_percent",
        )

        numbers = {}

        for field in numeric_fields:
            value = provenance[field]

            if isinstance(value, bool):
                raise ValueError(
                    f"{field} must be finite"
                )

            try:
                number = float(value)
            except (
                TypeError,
                ValueError,
                OverflowError,
            ):
                raise ValueError(
                    f"{field} must be finite"
                ) from None

            if not math.isfinite(number):
                raise ValueError(
                    f"{field} must be finite"
                )

            numbers[field] = number

        if numbers["best_price"] <= 0:
            raise ValueError(
                "best_price must be positive"
            )

        if numbers["average_price"] <= 0:
            raise ValueError(
                "average_price must be positive"
            )

        if numbers["available_liquidity"] < 0:
            raise ValueError(
                "available_liquidity must be non-negative"
            )

        if numbers["snapshot_spread_ms"] < 0:
            raise ValueError(
                "snapshot_spread_ms must be non-negative"
            )

        if (
            numbers["latest_timestamp"]
            < numbers["earliest_timestamp"]
        ):
            raise ValueError(
                "invalid snapshot timestamp range"
            )

        return {
            "route_id": route_id,
            "snapshot_count": snapshot_count,
            "symbols": normalized_symbols,
            "exchange_ids": (
                normalized_exchange_ids
            ),
            "earliest_timestamp": numbers[
                "earliest_timestamp"
            ],
            "latest_timestamp": numbers[
                "latest_timestamp"
            ],
            "snapshot_spread_ms": numbers[
                "snapshot_spread_ms"
            ],
            "entry_symbol": entry_symbol,
            "entry_side": entry_side,
            "available_liquidity": numbers[
                "available_liquidity"
            ],
            "best_price": numbers[
                "best_price"
            ],
            "average_price": numbers[
                "average_price"
            ],
            "slippage_percent": numbers[
                "slippage_percent"
            ],
        }

    @staticmethod
    def _required_text(
        value,
        field,
    ):
        if not isinstance(value, str):
            raise ValueError(
                f"{field} is required"
            )

        value = value.strip()

        if not value:
            raise ValueError(
                f"{field} is required"
            )

        return value
