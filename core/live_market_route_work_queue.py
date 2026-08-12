"""
ArbOS™
EX-200
Live Market Route Work Queue

Priority queue for market-event-driven route recalculation.

Maintains at most one active queued item per route.
Newer events replace older queued work for that route.
Stale and duplicate sequence events are rejected.

Paper-safe infrastructure only.
No authentication.
No transfers.
No live orders.
"""

import heapq


class LiveMarketRouteWorkQueue:
    def __init__(
        self,
        max_queue_size,
    ):
        if max_queue_size <= 0:
            raise ValueError(
                "max_queue_size must be positive"
            )

        self._max_queue_size = int(
            max_queue_size
        )

        self._heap = []
        self._active = {}
        self._sequence = 0

    def enqueue(
        self,
        request,
    ):
        route_id = request.get(
            "route_id"
        )

        if (
            route_id is None
            or not str(
                route_id
            ).strip()
        ):
            raise ValueError(
                "route_id is required"
            )

        route_id = str(
            route_id
        ).strip()

        incoming_sequence = request.get(
            "sequence"
        )

        existing = self._active.get(
            route_id
        )

        if existing is not None:
            existing_sequence = existing[
                "request"
            ].get(
                "sequence"
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
                        "queued": False,
                        "reason": (
                            "stale_route_event"
                        ),
                        "route_id": route_id,
                    }

                if (
                    incoming_sequence
                    == existing_sequence
                ):
                    return {
                        "queued": False,
                        "reason": (
                            "duplicate_route_event"
                        ),
                        "route_id": route_id,
                    }

            coalesced = True

        else:
            if (
                len(self._active)
                >= self._max_queue_size
            ):
                return {
                    "queued": False,
                    "reason": "queue_full",
                }

            coalesced = False

        priority = float(
            request.get(
                "priority",
                0.0,
            )
            or 0.0
        )

        self._sequence += 1

        generation = self._sequence

        record = {
            "generation": generation,
            "request": dict(
                request
            ),
        }

        self._active[
            route_id
        ] = record

        heapq.heappush(
            self._heap,
            (
                -priority,
                generation,
                route_id,
            ),
        )

        return {
            "queued": True,
            "coalesced": coalesced,
            "route_id": route_id,
            "priority": priority,
        }

    def dequeue(
        self,
    ):
        while self._heap:
            (
                _,
                generation,
                route_id,
            ) = heapq.heappop(
                self._heap
            )

            active = self._active.get(
                route_id
            )

            if active is None:
                continue

            if (
                active[
                    "generation"
                ]
                != generation
            ):
                continue

            request = dict(
                active[
                    "request"
                ]
            )

            del self._active[
                route_id
            ]

            return request

        return None

    def pending_count(
        self,
    ):
        return len(
            self._active
        )
