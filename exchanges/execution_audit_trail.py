from datetime import UTC, datetime


class ExecutionAuditTrail:
    def __init__(self):
        self._records = {}

    @staticmethod
    def _required(value, name):
        if value is None or not str(value).strip():
            raise ValueError(f"{name} is required")
        return str(value).strip()

    def record(self, execution_id, event, state, metadata=None):
        execution_id = self._required(execution_id, "execution_id")
        event = self._required(event, "event")
        state = self._required(state, "state")

        entry = {
            "execution_id": execution_id,
            "event": event,
            "state": state,
            "timestamp": datetime.now(UTC).isoformat(),
            "metadata": dict(metadata or {}),
        }

        self._records.setdefault(execution_id, []).append(entry)
        return dict(entry)

    def history(self, execution_id):
        execution_id = self._required(execution_id, "execution_id")
        return [
            dict(entry)
            for entry in self._records.get(execution_id, [])
        ]

    def latest(self, execution_id):
        records = self.history(execution_id)
        return records[-1] if records else None
