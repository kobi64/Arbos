"""
ArbOS™
EX-105
Opportunity Expiration Manager
"""

import time


class OpportunityExpirationManager:
    def __init__(self, ttl_seconds, clock=None):
        if ttl_seconds < 0:
            raise ValueError("ttl_seconds cannot be negative")

        self._ttl_seconds = float(ttl_seconds)
        self._clock = clock or time.time

    def evaluate(self, opportunity_id, created_at):
        if opportunity_id is None or not str(opportunity_id).strip():
            raise ValueError("opportunity_id is required")

        now = float(self._clock())
        age_seconds = now - float(created_at)
        expired = age_seconds >= self._ttl_seconds

        return {
            "opportunity_id": str(opportunity_id).strip(),
            "expired": expired,
            "reason": "opportunity_expired" if expired else None,
            "age_seconds": age_seconds,
            "ttl_seconds": self._ttl_seconds,
        }
