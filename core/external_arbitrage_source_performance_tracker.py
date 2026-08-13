"""
ArbOS™
EX-211
External Arbitrage Source Performance Tracker

Tracks attribution and performance of external arbitrage
signal sources.

Supports:
- first-source attribution
- multi-source contribution
- verification outcomes
- paper/live results
- realized profit
- source API cost
- net source value

No transfers.
No live orders.
"""

from copy import deepcopy


class ExternalArbitrageSourcePerformanceTracker:
    def __init__(self):
        self._opportunities = {}
        self._source_costs = {}
        self._triggered_discoveries = []

    def record_signal(
        self,
        opportunity_key,
        source,
        source_signal_id,
    ):
        opportunity_key = str(
            opportunity_key
            or ""
        ).strip()

        if not opportunity_key:
            raise ValueError(
                "opportunity_key is required"
            )

        source = str(
            source
            or ""
        ).strip().lower()

        if not source:
            raise ValueError(
                "source is required"
            )

        source_signal_id = str(
            source_signal_id
            or ""
        ).strip()

        if not source_signal_id:
            raise ValueError(
                "source_signal_id is required"
            )

        record = self._opportunities.get(
            opportunity_key
        )

        if record is None:
            record = {
                "opportunity_key": opportunity_key,
                "first_source": source,
                "sources": [],
                "source_signals": [],
                "source_signal_count": 0,
                "arbos_verified": False,
                "executable": False,
                "successful": False,
                "realized_profit": 0.0,
                "mode": None,
            }

            self._opportunities[
                opportunity_key
            ] = record

        if source not in record["sources"]:
            record["sources"].append(
                source
            )

        record["source_signals"].append({
            "source": source,
            "source_signal_id": (
                source_signal_id
            ),
        })

        record[
            "source_signal_count"
        ] += 1

        return {
            **deepcopy(record),
            "recorded": True,
            "paper_only": True,
            "live_order_submitted": False,
        }

    def get_opportunity(
        self,
        opportunity_key,
    ):
        record = self._opportunities.get(
            opportunity_key
        )

        if record is None:
            return None

        return deepcopy(
            record
        )

    def record_verification(
        self,
        opportunity_key,
        verified,
        executable,
    ):
        record = self._require_opportunity(
            opportunity_key
        )

        record["arbos_verified"] = bool(
            verified
        )

        record["executable"] = bool(
            executable
        )

        return {
            **deepcopy(record),
            "paper_only": True,
            "live_order_submitted": False,
        }

    def record_result(
        self,
        opportunity_key,
        successful,
        realized_profit,
        mode,
    ):
        record = self._require_opportunity(
            opportunity_key
        )

        record["successful"] = bool(
            successful
        )

        record["realized_profit"] = float(
            realized_profit
        )

        record["mode"] = str(
            mode
            or ""
        ).strip().lower()

        return {
            **deepcopy(record),
            "paper_only": True,
            "live_order_submitted": False,
        }

    def record_triggered_discovery(
        self,
        source,
        trigger_opportunity_key,
        discovered_opportunity_key,
        successful,
        realized_profit,
        mode,
    ):
        source = str(
            source
            or ""
        ).strip().lower()

        if not source:
            raise ValueError(
                "source is required"
            )

        trigger_opportunity_key = str(
            trigger_opportunity_key
            or ""
        ).strip()

        if not trigger_opportunity_key:
            raise ValueError(
                "trigger_opportunity_key is required"
            )

        discovered_opportunity_key = str(
            discovered_opportunity_key
            or ""
        ).strip()

        if not discovered_opportunity_key:
            raise ValueError(
                "discovered_opportunity_key is required"
            )

        record = {
            "trigger_source": source,
            "trigger_opportunity_key": (
                trigger_opportunity_key
            ),
            "discovered_opportunity_key": (
                discovered_opportunity_key
            ),
            "discovery_source": "arbos_native",
            "direct_external_discovery": False,
            "successful": bool(
                successful
            ),
            "realized_profit": float(
                realized_profit
            ),
            "mode": str(
                mode
                or ""
            ).strip().lower(),
        }

        self._triggered_discoveries.append(
            record
        )

        return {
            **deepcopy(record),
            "recorded": True,
            "paper_only": True,
            "live_order_submitted": False,
        }

    def set_source_cost(
        self,
        source,
        monthly_cost,
    ):
        source = str(
            source
            or ""
        ).strip().lower()

        if not source:
            raise ValueError(
                "source is required"
            )

        monthly_cost = float(
            monthly_cost
        )

        if monthly_cost < 0:
            raise ValueError(
                "monthly_cost cannot be negative"
            )

        self._source_costs[
            source
        ] = monthly_cost

        return {
            "source": source,
            "monthly_cost": monthly_cost,
            "paper_only": True,
            "live_order_submitted": False,
        }

    def source_statistics(
        self,
        source,
    ):
        source = str(
            source
            or ""
        ).strip().lower()

        signals = 0
        verified = 0
        successful = 0
        first_source_successes = 0
        gross_profit = 0.0

        for record in (
            self._opportunities.values()
        ):
            if source not in record[
                "sources"
            ]:
                continue

            signals += sum(
                1
                for signal in record[
                    "source_signals"
                ]
                if signal[
                    "source"
                ] == source
            )

            if record[
                "arbos_verified"
            ]:
                verified += 1

            if record[
                "successful"
            ]:
                successful += 1
                gross_profit += float(
                    record[
                        "realized_profit"
                    ]
                )

                if (
                    record[
                        "first_source"
                    ]
                    == source
                ):
                    first_source_successes += 1

        direct_successful = 0
        direct_profit = 0.0

        for record in (
            self._opportunities.values()
        ):
            if source not in record[
                "sources"
            ]:
                continue

            if record[
                "successful"
            ]:
                direct_successful += 1
                direct_profit += float(
                    record[
                        "realized_profit"
                    ]
                )

        triggered_native_successful = 0
        triggered_native_profit = 0.0

        for record in (
            self._triggered_discoveries
        ):
            if (
                record[
                    "trigger_source"
                ]
                != source
            ):
                continue

            if record[
                "successful"
            ]:
                triggered_native_successful += 1
                triggered_native_profit += float(
                    record[
                        "realized_profit"
                    ]
                )

        total_source_value = (
            direct_profit
            + triggered_native_profit
        )

        monthly_cost = float(
            self._source_costs.get(
                source,
                0.0,
            )
        )

        return {
            "source": source,
            "signals": signals,
            "verified": verified,
            "successful": successful,
            "first_source_successes": (
                first_source_successes
            ),
            "gross_attributed_profit": (
                gross_profit
            ),
            "direct_successful": (
                direct_successful
            ),
            "direct_profit": (
                direct_profit
            ),
            "triggered_native_successful": (
                triggered_native_successful
            ),
            "triggered_native_profit": (
                triggered_native_profit
            ),
            "total_source_value": (
                total_source_value
            ),
            "monthly_api_cost": (
                monthly_cost
            ),
            "net_value_after_api_cost": (
                gross_profit
                - monthly_cost
            ),
            "paper_only": True,
            "live_order_submitted": False,
        }

    def _require_opportunity(
        self,
        opportunity_key,
    ):
        record = self._opportunities.get(
            opportunity_key
        )

        if record is None:
            raise ValueError(
                "opportunity not found"
            )

        return record
