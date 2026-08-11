"""
ArbOS™
EX-193
Native Coverage Health History Store

Persists native coverage health reports as append-only JSONL.

Observability/persistence only.
No authentication.
No transfers.
No live orders.
"""

import json
import time
from pathlib import Path


class NativeCoverageHealthHistoryStore:
    def __init__(
        self,
        path,
        clock=None,
    ):
        if path is None:
            raise ValueError(
                "path is required"
            )

        self._path = Path(path)
        self._clock = (
            clock
            if clock is not None
            else time.time
        )

    def append(
        self,
        health_report,
    ):
        if health_report is None:
            raise ValueError(
                "health_report is required"
            )

        timestamp = float(
            self._clock()
        )

        record = {
            "timestamp": timestamp,
            "report": dict(
                health_report
            ),
        }

        self._path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        with self._path.open(
            "a",
            encoding="utf-8",
        ) as handle:
            handle.write(
                json.dumps(
                    record,
                    sort_keys=True,
                )
            )
            handle.write("\n")

        return {
            "stored": True,
            "timestamp": timestamp,
            "status": health_report.get(
                "status"
            ),
            "live_order_submitted": False,
        }

    def history(
        self,
        limit=None,
    ):
        if (
            limit is not None
            and (
                not isinstance(
                    limit,
                    int,
                )
                or isinstance(
                    limit,
                    bool,
                )
                or limit <= 0
            )
        ):
            raise ValueError(
                "limit must be positive"
            )

        if not self._path.exists():
            return []

        records = []

        with self._path.open(
            "r",
            encoding="utf-8",
        ) as handle:
            for line in handle:
                line = line.strip()

                if not line:
                    continue

                records.append(
                    json.loads(line)
                )

        if limit is not None:
            records = records[
                -limit:
            ]

        return records

    def latest(self):
        history = self.history(
            limit=1
        )

        if not history:
            return None

        return history[0]
