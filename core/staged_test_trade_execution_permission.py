"""
ArbOS™
EX-154
Staged Test Trade Execution Permission

Creates and grants a single-use execution permission for an
approved staged test-trade handoff.

This module does not execute trades or submit live orders.
"""


class StagedTestTradeExecutionPermission:
    def __init__(self):
        self._counter = 0
        self._pending = {}

    def create(
        self,
        handoff_result,
    ):
        if handoff_result is None:
            raise ValueError(
                "handoff_result is required"
            )

        if handoff_result.get(
            "live_order_submitted"
        ) is True:
            return {
                "permission_granted": False,
                "status": "blocked",
                "reason": "live_order_already_submitted",
                "live_order_submitted": True,
            }

        if handoff_result.get(
            "handoff_ready"
        ) is not True:
            return {
                "permission_granted": False,
                "status": "blocked",
                "reason": "handoff_not_ready",
                "live_order_submitted": False,
            }

        self._counter += 1

        permission_id = (
            f"PERM-{self._counter:03d}"
        )

        record = {
            "permission_id": permission_id,
            "route_id": handoff_result.get(
                "route_id"
            ),
            "approval_id": handoff_result.get(
                "approval_id"
            ),
            "asset": handoff_result.get(
                "asset"
            ),
            "trade_amount": float(
                handoff_result.get(
                    "trade_amount",
                    0.0,
                )
            ),
        }

        self._pending[
            permission_id
        ] = record

        return {
            **record,
            "permission_granted": False,
            "status": (
                "awaiting_execution_permission"
            ),
            "live_order_submitted": False,
        }

    def grant(
        self,
        permission_id,
        trade_amount,
    ):
        if permission_id not in self._pending:
            return {
                "permission_id": permission_id,
                "permission_granted": False,
                "status": "not_found",
                "live_order_submitted": False,
            }

        record = self._pending[
            permission_id
        ]

        expected_amount = float(
            record["trade_amount"]
        )

        supplied_amount = float(
            trade_amount
        )

        if supplied_amount != expected_amount:
            return {
                **record,
                "permission_granted": False,
                "status": "blocked",
                "reason": "trade_amount_mismatch",
                "live_order_submitted": False,
            }

        self._pending.pop(
            permission_id,
            None,
        )

        return {
            **record,
            "permission_granted": True,
            "status": (
                "execution_permission_granted"
            ),
            "live_order_submitted": False,
        }
