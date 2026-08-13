"""
ArbOS™
EX-215
Live Multi-Source Intelligence Cycle

Runs one live external-intelligence collection cycle through
the existing EX-214 multi-source orchestrator.

Responsibilities:
- run the multi-source orchestrator once
- preserve source-level results
- preserve grouped/ranked opportunities
- record cycle observation time
- maintain paper-safe boundaries

No authentication changes.
No transfers.
No live orders.
"""

import time
from copy import deepcopy


class LiveMultiSourceIntelligenceCycle:
    def __init__(
        self,
        orchestrator,
        clock=None,
    ):
        if orchestrator is None:
            raise ValueError(
                "orchestrator is required"
            )

        self._orchestrator = orchestrator
        self._clock = clock or time.time

    def run_once(self):
        observed_at = float(
            self._clock()
        )

        result = (
            self._orchestrator.run_once()
        )

        opportunities = []

        for opportunity in (
            result.get(
                "opportunities"
            )
            or []
        ):
            record = deepcopy(
                opportunity
            )

            # External intelligence remains
            # unverified until the dedicated
            # ArbOS™ verification phase runs.
            record[
                "arbos_verified"
            ] = False

            record[
                "executable"
            ] = False

            record[
                "verification_required"
            ] = True

            record[
                "paper_only"
            ] = True

            record[
                "live_order_submitted"
            ] = False

            opportunities.append(
                record
            )

        return {
            **deepcopy(result),
            "cycle_observed_at": (
                observed_at
            ),
            "opportunities": (
                opportunities
            ),
            "paper_only": True,
            "live_order_submitted": False,
        }
