"""
ArbOS™
EX-024
Execution Engine Foundation

Controlled execution lifecycle manager.

Responsibilities:
- Create execution requests
- Require approval before execution
- Track execution states
- Record completion, failure and cancellation
"""

import math


class ExecutionEngine:

    _executions = {}

    @classmethod
    def create_request(
        cls,
        approval_status: str,
        asset: str,
        amount: float,
        route: str,
    ):
        if not isinstance(asset, str) or not asset.strip():
            raise ValueError("asset is required")

        if isinstance(amount, bool):
            raise ValueError("invalid execution amount")

        try:
            amount = float(amount)
        except (TypeError, ValueError, OverflowError):
            raise ValueError("invalid execution amount")

        if not math.isfinite(amount) or amount <= 0:
            raise ValueError("invalid execution amount")

        if not isinstance(route, str) or not route.strip():
            raise ValueError("route is required")

        if approval_status != "approved":
            return {
                "status": "blocked",
                "reason": "approval_required",
            }

        execution_id = f"EXEC-{len(cls._executions) + 1:03d}"

        cls._executions[execution_id] = {
            "asset": asset,
            "amount": amount,
            "route": route,
            "execution_state": "CREATED",
        }

        return {
            "execution_id": execution_id,
            "status": "created",
            "execution_state": "CREATED",
        }

    @classmethod
    def start_execution(cls, execution_id: str):
        cls._executions[execution_id] = {
            "execution_state": "EXECUTING"
        }

        return {
            "status": "executing",
            "execution_state": "EXECUTING",
            "execution_id": execution_id,
        }

    @classmethod
    def complete_execution(cls, execution_id: str):
        cls._executions[execution_id] = {
            "execution_state": "COMPLETED"
        }

        return {
            "status": "completed",
            "execution_state": "COMPLETED",
            "execution_id": execution_id,
        }

    @classmethod
    def fail_execution(cls, execution_id: str, reason: str):
        cls._executions[execution_id] = {
            "execution_state": "FAILED",
            "reason": reason,
        }

        return {
            "status": "failed",
            "execution_state": "FAILED",
            "execution_id": execution_id,
            "reason": reason,
        }

    @classmethod
    def cancel_execution(cls, execution_id: str, reason: str):
        cls._executions[execution_id] = {
            "execution_state": "CANCELLED",
            "reason": reason,
        }

        return {
            "status": "cancelled",
            "execution_state": "CANCELLED",
            "execution_id": execution_id,
            "reason": reason,
        }
