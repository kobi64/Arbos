"""
ArbOS™
EX-084
Safe Live Paper Replay Engine
"""


class SafeLivePaperReplayEngine:
    def __init__(self):
        self._history = []

    def replay(self, audit_record):
        if audit_record is None:
            raise ValueError("audit_record is required")

        if "record_id" not in audit_record:
            raise ValueError("record_id is required")

        if "opportunity_id" not in audit_record:
            raise ValueError("opportunity_id is required")

        result = {
            "record_id": audit_record["record_id"],
            "opportunity_id": audit_record["opportunity_id"],
            "replayed": True,
            "readiness": audit_record.get("readiness"),
            "approval": audit_record.get("approval"),
            "execution": audit_record.get("execution"),
            "pnl": audit_record.get("pnl"),
        }

        self._history.append(dict(result))

        return dict(result)

    def history(self):
        return [dict(record) for record in self._history]
