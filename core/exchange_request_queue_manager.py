"""
ArbOS™
EX-111
Exchange Request Queue Manager
"""

import heapq
import math


class ExchangeRequestQueueManager:
    def __init__(self, max_queue_size, clock=None):
        if max_queue_size <= 0:
            raise ValueError("max_queue_size must be positive")

        self._max_queue_size = int(max_queue_size)
        self._clock = clock
        self._queue = []
        self._sequence = 0

    def enqueue(self, request):
        request_id = request.get("request_id")

        if request_id is None or not str(request_id).strip():
            raise ValueError("request_id is required")

        if len(self._queue) >= self._max_queue_size:
            return {
                "queued": False,
                "reason": "queue_full",
            }

        request_id = str(request_id).strip()
        raw_priority = request.get("priority", 0.0)

        if isinstance(raw_priority, bool):
            raise ValueError("priority must be a finite number")

        try:
            priority = float(raw_priority)
        except (TypeError, ValueError):
            raise ValueError("priority must be a finite number")

        if not math.isfinite(priority):
            raise ValueError("priority must be a finite number")

        self._sequence += 1

        heapq.heappush(
            self._queue,
            (-priority, self._sequence, dict(request)),
        )

        return {
            "queued": True,
            "request_id": request_id,
            "priority": priority,
        }

    def dequeue(self):
        if not self._queue:
            return None

        _, _, request = heapq.heappop(self._queue)
        return dict(request)

    def pending_count(self):
        return len(self._queue)
