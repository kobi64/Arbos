"""
ArbOS™
EX-057
Execution Idempotency & Duplicate-Order Protection
"""


class ExecutionIdempotencyGuard:
    def __init__(self):
        self._execution_ids = set()

    def _normalize(self, execution_id):
        if execution_id is None:
            raise ValueError("execution_id is required")

        execution_id = str(execution_id).strip()

        if not execution_id:
            raise ValueError("execution_id is required")

        return execution_id

    def register(self, execution_id):
        execution_id = self._normalize(execution_id)

        if execution_id in self._execution_ids:
            return {
                "accepted": False,
                "duplicate": True,
                "reason": "DUPLICATE_EXECUTION",
            }

        self._execution_ids.add(execution_id)

        return {
            "accepted": True,
            "duplicate": False,
            "reason": None,
        }

    def release(self, execution_id):
        execution_id = self._normalize(execution_id)

        if execution_id not in self._execution_ids:
            return False

        self._execution_ids.remove(execution_id)
        return True

    def contains(self, execution_id):
        execution_id = self._normalize(execution_id)
        return execution_id in self._execution_ids

    def clear(self):
        self._execution_ids.clear()
