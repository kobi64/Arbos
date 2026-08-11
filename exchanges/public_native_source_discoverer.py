"""
ArbOS™
EX-188
Public Native Source Discoverer

Inspects an exchange adapter for public market-catalogue methods
without executing those methods.

Discovery only.
No authentication.
No transfers.
No live orders.
No public API calls.
"""


class PublicNativeSourceDiscoverer:
    def discover(
        self,
        exchange,
    ):
        if exchange is None:
            raise ValueError(
                "exchange is required"
            )

        exchange_id = str(
            getattr(
                exchange,
                "id",
                "",
            )
            or ""
        ).strip().lower()

        candidates = []

        for name in dir(exchange):
            lower = name.lower()

            if not lower.startswith("public"):
                continue

            method = getattr(
                exchange,
                name,
                None,
            )

            if not callable(method):
                continue

            if any(
                token in lower
                for token in (
                    "orderbook",
                    "order_book",
                    "depth",
                    "ticker",
                    "trade",
                    "candle",
                    "kline",
                )
            ):
                continue

            if not any(
                token in lower
                for token in (
                    "symbol",
                    "symbols",
                    "market",
                    "markets",
                    "pair",
                    "pairs",
                    "instrument",
                    "instruments",
                )
            ):
                continue

            candidates.append(
                name
            )

        candidates = sorted(
            set(candidates)
        )

        return {
            "exchange_id": exchange_id,
            "candidate_methods": candidates,
            "candidate_count": len(
                candidates
            ),
            "discovery_complete": True,
            "live_order_submitted": False,
        }
