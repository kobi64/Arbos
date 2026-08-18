"""
ArbOS™
EX-102
Live Opportunity Intake Service
"""

import math


class LiveOpportunityIntakeService:
    def __init__(self, scheduler):
        if scheduler is None:
            raise ValueError("scheduler is required")

        self._scheduler = scheduler
        self._received_ids = set()
        self._received = 0
        self._accepted = 0
        self._rejected = 0

    def submit(self, opportunity):
        self._received += 1

        opportunity_id = opportunity.get("opportunity_id")

        if opportunity_id is None or not str(opportunity_id).strip():
            self._rejected += 1
            raise ValueError("opportunity_id is required")

        if opportunity.get("route") is None:
            self._rejected += 1
            raise ValueError("route is required")

        opportunity_id = str(opportunity_id).strip()

        if opportunity_id in self._received_ids:
            self._rejected += 1
            raise ValueError("opportunity_id already received")

        self._received_ids.add(opportunity_id)

        queued = self._scheduler.enqueue(dict(opportunity))

        if "priority" not in queued:
            self._rejected += 1
            raise ValueError("scheduler priority is required")

        raw_priority = queued["priority"]

        if isinstance(raw_priority, bool):
            self._rejected += 1
            raise ValueError(
                "scheduler priority must be a finite number"
            )

        try:
            priority = float(raw_priority)
        except (TypeError, ValueError):
            self._rejected += 1
            raise ValueError(
                "scheduler priority must be a finite number"
            )

        if not math.isfinite(priority):
            self._rejected += 1
            raise ValueError(
                "scheduler priority must be a finite number"
            )

        self._accepted += 1

        return {
            "accepted": True,
            "queued": queued["queued"],
            "opportunity_id": opportunity_id,
            "priority": priority,
        }

    def statistics(self):
        return {
            "received": self._received,
            "accepted": self._accepted,
            "rejected": self._rejected,
        }
