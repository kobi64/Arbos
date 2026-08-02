"""
ArbOS™
EX-026
Execution Recovery & Failure Handling

Handles failed executions, recovery states,
retry tracking, and recovery outcomes.
"""

from datetime import datetime, UTC


class ExecutionRecovery:

    _history = {}
    _retry_count = {}

    VALID_STATES = {
        "RECOVERY_PENDING",
        "RETRYING",
        "RECOVERED",
        "FAILED",
    }

    @classmethod
    def create_record(
        cls,
        execution_id: str,
        reason: str,
    ):
        if not execution_id:
            raise ValueError("execution_id is required")

        if not reason:
            raise ValueError("reason is required")

        cls._history[execution_id] = [
            {
                "timestamp": datetime.now(UTC).isoformat(),
                "event": "RECOVERY_CREATED",
                "reason": reason,
            }
        ]

        cls._retry_count[execution_id] = 0

        return {
            "status": "recovery_created",
            "execution_id": execution_id,
        }

    @classmethod
    def set_recovery_state(
        cls,
        execution_id: str,
        state: str,
    ):
        if state not in cls.VALID_STATES:
            raise ValueError("invalid recovery state")

        if execution_id not in cls._history:
            cls._history[execution_id] = []

        cls._history[execution_id].append(
            {
                "timestamp": datetime.now(UTC).isoformat(),
                "event": "STATE_CHANGE",
                "state": state,
            }
        )

        return {
            "state": state,
        }

    @classmethod
    def record_retry(
        cls,
        execution_id: str,
    ):
        if execution_id not in cls._retry_count:
            cls._retry_count[execution_id] = 0

        cls._retry_count[execution_id] += 1

        if execution_id not in cls._history:
            cls._history[execution_id] = []

        cls._history[execution_id].append(
            {
                "timestamp": datetime.now(UTC).isoformat(),
                "event": "RETRY",
                "attempt": cls._retry_count[execution_id],
            }
        )

        return {
            "status": "retry_recorded",
            "attempt": cls._retry_count[execution_id],
        }

    @classmethod
    def complete_recovery(
        cls,
        execution_id: str,
        outcome: str,
    ):
        if execution_id not in cls._history:
            cls._history[execution_id] = []

        cls._history[execution_id].append(
            {
                "timestamp": datetime.now(UTC).isoformat(),
                "event": "RECOVERED",
                "outcome": outcome,
            }
        )

        return {
            "status": "recovered",
            "outcome": outcome,
        }

    @classmethod
    def fail_recovery(
        cls,
        execution_id: str,
        reason: str,
    ):
        if execution_id not in cls._history:
            cls._history[execution_id] = []

        cls._history[execution_id].append(
            {
                "timestamp": datetime.now(UTC).isoformat(),
                "event": "FAILED",
                "reason": reason,
            }
        )

        return {
            "status": "failed",
            "reason": reason,
        }

    @classmethod
    def get_history(
        cls,
        execution_id: str,
    ):
        return cls._history.get(execution_id, [])
