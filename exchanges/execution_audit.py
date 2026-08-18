"""
ArbOS™
EX-025
Execution Audit Trail

Permanent execution event tracking layer.
"""

from datetime import datetime, UTC
import math


class ExecutionAudit:

    _history = {}

    VALID_STATES = {
        "CREATED",
        "APPROVED",
        "EXECUTING",
        "COMPLETED",
        "FAILED",
        "CANCELLED",
    }

    @classmethod
    def create_record(cls, execution_id, asset, amount, route):
        if not execution_id:
            raise ValueError("execution_id is required")

        if not asset:
            raise ValueError("asset is required")

        if isinstance(amount, bool):
            raise ValueError("invalid amount")

        try:
            amount = float(amount)
        except (TypeError, ValueError, OverflowError):
            raise ValueError("invalid amount")

        if not math.isfinite(amount) or amount <= 0:
            raise ValueError("invalid amount")

        if not route:
            raise ValueError("route is required")

        cls._history[execution_id] = [
            {
                "timestamp": datetime.now(UTC).isoformat(),
                "event": "CREATED",
                "asset": asset,
                "amount": amount,
                "route": route,
            }
        ]

        return {
            "status": "recorded",
            "execution_id": execution_id,
        }

    @classmethod
    def record_state(cls, execution_id, state):
        if not execution_id:
            raise ValueError("execution_id is required")

        if state not in cls.VALID_STATES:
            raise ValueError("invalid state")

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
            "status": "recorded",
            "state": state,
        }

    @classmethod
    def record_completion(cls, execution_id, profit):
        if execution_id not in cls._history:
            cls._history[execution_id] = []

        cls._history[execution_id].append(
            {
                "timestamp": datetime.now(UTC).isoformat(),
                "event": "COMPLETED",
                "profit": profit,
            }
        )

        return {
            "status": "completed",
            "profit": profit,
        }

    @classmethod
    def record_failure(cls, execution_id, reason):
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
    def get_history(cls, execution_id):
        return cls._history.get(execution_id, [])
