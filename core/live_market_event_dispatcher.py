"""
ArbOS™
EX-200
Live Market Event Dispatcher

Maps market-data updates to only the routes affected by
those updates and enqueues route recalculation work.

This is metadata/work-dispatch infrastructure only.

Paper-safe.
No authentication.
No transfers.
No live orders.
"""


class LiveMarketEventDispatcher:
    def __init__(
        self,
        work_queue,
    ):
        if work_queue is None:
            raise ValueError(
                "work_queue is required"
            )

        self._work_queue = work_queue
        self._market_routes = {}
        self._route_markets = {}

    def register_route(
        self,
        route_id,
        markets,
    ):
        route_id = str(
            route_id
            or ""
        ).strip()

        if not route_id:
            raise ValueError(
                "route_id is required"
            )

        normalized_markets = set()

        for market in markets or []:
            if (
                not isinstance(
                    market,
                    (tuple, list),
                )
                or len(market) != 2
            ):
                raise ValueError(
                    "market dependency must be "
                    "(exchange_id, symbol)"
                )

            key = self._normalize_market_key(
                exchange_id=market[0],
                symbol=market[1],
            )

            normalized_markets.add(
                key
            )

        self._route_markets[
            route_id
        ] = normalized_markets

        for key in normalized_markets:
            self._market_routes.setdefault(
                key,
                set(),
            ).add(
                route_id
            )

        return {
            "registered": True,
            "route_id": route_id,
            "market_count": len(
                normalized_markets
            ),
        }

    def dispatch(
        self,
        event,
    ):
        if event is None:
            raise ValueError(
                "event is required"
            )

        exchange_id = event.get(
            "exchange_id"
        )

        if (
            exchange_id is None
            or not str(
                exchange_id
            ).strip()
        ):
            raise ValueError(
                "exchange_id is required"
            )

        symbol = event.get(
            "symbol"
        )

        if (
            symbol is None
            or not str(
                symbol
            ).strip()
        ):
            raise ValueError(
                "symbol is required"
            )

        key = self._normalize_market_key(
            exchange_id=exchange_id,
            symbol=symbol,
        )

        affected_route_ids = sorted(
            self._market_routes.get(
                key,
                set(),
            )
        )

        priority = float(
            event.get(
                "priority",
                0.0,
            )
            or 0.0
        )

        sequence = event.get(
            "sequence"
        )

        queued_route_ids = []

        for route_id in affected_route_ids:
            request_id = self._build_request_id(
                route_id=route_id,
                exchange_id=key[0],
                symbol=key[1],
                sequence=sequence,
            )

            work_item = {
                "request_id": request_id,
                "route_id": route_id,
                "exchange_id": key[0],
                "symbol": key[1],
                "sequence": sequence,
                "priority": priority,
                "event": dict(
                    event
                ),
                "paper_only": True,
                "live_order_submitted": False,
            }

            result = self._work_queue.enqueue(
                work_item
            )

            if result.get(
                "queued"
            ) is True:
                queued_route_ids.append(
                    route_id
                )

        return {
            "exchange_id": key[0],
            "symbol": key[1],
            "sequence": sequence,
            "affected_route_count": len(
                affected_route_ids
            ),
            "affected_route_ids": (
                affected_route_ids
            ),
            "queued_route_count": len(
                queued_route_ids
            ),
            "queued_route_ids": (
                queued_route_ids
            ),
            "paper_only": True,
            "live_order_submitted": False,
        }

    def routes_for_market(
        self,
        exchange_id,
        symbol,
    ):
        key = self._normalize_market_key(
            exchange_id=exchange_id,
            symbol=symbol,
        )

        return sorted(
            self._market_routes.get(
                key,
                set(),
            )
        )

    def markets_for_route(
        self,
        route_id,
    ):
        route_id = str(
            route_id
            or ""
        ).strip()

        return sorted(
            self._route_markets.get(
                route_id,
                set(),
            )
        )

    @staticmethod
    def _normalize_market_key(
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

    @staticmethod
    def _build_request_id(
        route_id,
        exchange_id,
        symbol,
        sequence,
    ):
        sequence_part = (
            str(sequence)
            if sequence is not None
            else "NA"
        )

        symbol_part = (
            str(symbol)
            .replace("/", "-")
            .replace(":", "-")
        )

        return (
            f"MARKET-EVENT-"
            f"{exchange_id}-"
            f"{symbol_part}-"
            f"{route_id}-"
            f"{sequence_part}"
        )
