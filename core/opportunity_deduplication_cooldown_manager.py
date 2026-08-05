"""
ArbOS™
EX-103
Opportunity Deduplication & Cooldown Manager
"""

import time


class OpportunityDeduplicationCooldownManager:
    def __init__(self, cooldown_seconds, clock=None):
        if cooldown_seconds < 0:
            raise ValueError("cooldown_seconds cannot be negative")

        self._cooldown_seconds = float(cooldown_seconds)
        self._clock = clock or time.time
        self._last_seen = {}
        self._accepted = 0
        self._rejected = 0

    def evaluate(self, opportunity_id):
        if opportunity_id is None or not str(opportunity_id).strip():
            raise ValueError("opportunity_id is required")

        opportunity_id = str(opportunity_id).strip()
        now = float(self._clock())
        last_seen = self._last_seen.get(opportunity_id)

        if last_seen is not None:
            elapsed = now - last_seen

            if elapsed < self._cooldown_seconds:
                self._rejected += 1
                return {
                    "accepted": False,
                    "reason": "cooldown_active",
                    "remaining_seconds": (
                        self._cooldown_seconds - elapsed
                    ),
                }

        self._last_seen[opportunity_id] = now
        self._accepted += 1

        return {
            "accepted": True,
            "reason": None,
            "remaining_seconds": 0.0,
        }

    def statistics(self):
        return {
            "accepted": self._accepted,
            "rejected": self._rejected,
        }
