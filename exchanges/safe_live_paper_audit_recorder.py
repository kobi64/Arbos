"""
ArbOS™
EX-083
Safe Live Paper Audit Recorder
"""

from datetime import datetime, UTC
from uuid import uuid4


class SafeLivePaperAuditRecorder:
    def __init__(self):
        self._history = []

    def record_decision(
        self,
        opportunity_id,
        readiness,
        approval,
        execution,
        pnl,
    ):
        if not opportunity_id:
            raise ValueError("opportunity_id is required")

        record = {
            "record_id": str(uuid4()),
            "timestamp": datetime.now(UTC).isoformat(),
            "opportunity_id": opportunity_id,
            "readiness": readiness,
            "approval": approval,
            "execution": execution,
            "pnl": pnl,
        }

        self._history.append(dict(record))

        return dict(record)

    def history(self):
        return [dict(record) for record in self._history]
