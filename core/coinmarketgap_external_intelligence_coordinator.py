"""
ArbOS™
EX-211
CoinMarketGap External Intelligence Coordinator

Coordinates one CoinMarketGap intelligence ingestion cycle.

Flow:
- fetch exploitable CoinMarketGap rows
- adapt source-specific fields
- normalize into ArbOS™ external signal format
- deduplicate intake
- correlate directional opportunities
- record source attribution
- return verification candidates

External signals remain leads only.
No live orders.
"""

import time


class CoinMarketGapExternalIntelligenceCoordinator:
    def __init__(
        self,
        client,
        adapter,
        normalizer,
        intake,
        correlator,
        tracker,
        clock=None,
    ):
        if client is None:
            raise ValueError(
                "client is required"
            )

        if adapter is None:
            raise ValueError(
                "adapter is required"
            )

        if normalizer is None:
            raise ValueError(
                "normalizer is required"
            )

        if intake is None:
            raise ValueError(
                "intake is required"
            )

        if correlator is None:
            raise ValueError(
                "correlator is required"
            )

        if tracker is None:
            raise ValueError(
                "tracker is required"
            )

        self._client = client
        self._adapter = adapter
        self._normalizer = normalizer
        self._intake = intake
        self._correlator = correlator
        self._tracker = tracker
        self._clock = clock or time.time

    def run_once(
        self,
    ):
        fetch_result = (
            self._client.fetch(
                exploitable_only=True
            )
        )

        if (
            fetch_result.get(
                "fetch_complete"
            )
            is not True
        ):
            return {
                "fetch_complete": False,
                "candidate_count": 0,
                "duplicate_count": 0,
                "candidates": [],
                "paper_only": True,
                "live_order_submitted": False,
            }

        observed_at = float(
            self._clock()
        )

        candidates = []
        duplicate_count = 0

        for row in (
            fetch_result.get(
                "results"
            )
            or []
        ):
            adapted = (
                self._adapter.adapt(
                    row,
                    observed_at=(
                        observed_at
                    ),
                )
            )

            normalized = (
                self._normalizer.normalize(
                    source="coinmarketgap",
                    signal=adapted,
                )
            )

            intake_result = (
                self._intake.submit(
                    normalized
                )
            )

            if (
                intake_result.get(
                    "accepted"
                )
                is not True
            ):
                if (
                    intake_result.get(
                        "reason"
                    )
                    == "duplicate_external_signal"
                ):
                    duplicate_count += 1

                continue

            correlation = (
                self._correlator.correlate(
                    normalized
                )
            )

            opportunity_key = (
                correlation[
                    "opportunity_key"
                ]
            )

            self._tracker.record_signal(
                opportunity_key=(
                    opportunity_key
                ),
                source=(
                    normalized[
                        "source"
                    ]
                ),
                source_signal_id=(
                    normalized[
                        "source_signal_id"
                    ]
                ),
            )

            candidate = dict(
                normalized
            )

            candidate[
                "opportunity_key"
            ] = opportunity_key

            candidate[
                "correlated_sources"
            ] = list(
                correlation.get(
                    "sources"
                )
                or []
            )

            candidate[
                "arbos_verified"
            ] = False

            candidate[
                "executable"
            ] = False

            candidate[
                "verification_required"
            ] = True

            candidate[
                "paper_only"
            ] = True

            candidate[
                "live_order_submitted"
            ] = False

            candidates.append(
                candidate
            )

        return {
            "fetch_complete": True,
            "candidate_count": len(
                candidates
            ),
            "duplicate_count": (
                duplicate_count
            ),
            "candidates": candidates,
            "paper_only": True,
            "live_order_submitted": False,
        }
