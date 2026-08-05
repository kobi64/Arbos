"""
ArbOS™
EX-099
Continuous Opportunity Scheduler
"""

import heapq


class ContinuousOpportunityScheduler:
    def __init__(self, coordinator):
        self._coordinator = coordinator
        self._queue = []
        self._queued_ids = set()
        self._sequence = 0

    def enqueue(self, opportunity):
        opportunity_id = opportunity.get("opportunity_id")

        if opportunity_id is None or not str(opportunity_id).strip():
            raise ValueError("opportunity_id is required")

        opportunity_id = str(opportunity_id).strip()

        if opportunity_id in self._queued_ids:
            raise ValueError("opportunity_id already queued")

        priority = float(opportunity.get("priority", 0.0))
        self._sequence += 1

        heapq.heappush(
            self._queue,
            (-priority, self._sequence, dict(opportunity)),
        )
        self._queued_ids.add(opportunity_id)

        return {
            "queued": True,
            "opportunity_id": opportunity_id,
            "priority": priority,
        }

    def process_next(self):
        if not self._queue:
            return None

        _, _, opportunity = heapq.heappop(self._queue)
        opportunity_id = str(opportunity["opportunity_id"]).strip()
        self._queued_ids.discard(opportunity_id)

        return self._coordinator.execute(opportunity)

    def pending_count(self):
        return len(self._queue)
