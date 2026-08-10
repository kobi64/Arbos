"""
ArbOS™
EX-171
Live Paper Repeat / Scale Cycle Orchestration

Coordinates a freshly permitted repeat/scale staged test trade
through the existing atomic live-market paper route orchestrator.

The execution permission must match the exact route starting value.

Real market snapshots may be consumed.
All execution remains simulated and paper-only.

This module never submits a live exchange order.
"""

from exchanges.live_paper_trading_orchestrator import (
    LivePaperTradingOrchestrator,
)


class LivePaperRepeatScaleCycleOrchestration:
    def __init__(self, snapshot_engine):
        if snapshot_engine is None:
            raise ValueError(
                "snapshot_engine is required"
            )

        self._orchestrator = (
            LivePaperTradingOrchestrator(
                snapshot_engine
            )
        )
        self._history = []

    def execute(
        self,
        permission_result,
        execution_id,
        route,
        portfolio,
        asset,
        additional_exposure,
        starting_value,
    ):
        if permission_result is None:
            raise ValueError(
                "permission_result is required"
            )

        if route is None:
            raise ValueError(
                "route is required"
            )

        if permission_result.get(
            "live_order_submitted"
        ) is True:
            return self._blocked(
                reason="live_order_already_submitted"
            )

        if permission_result.get(
            "permission_granted"
        ) is not True:
            return self._blocked(
                reason="execution_permission_required"
            )

        if (
            permission_result.get("status")
            != "execution_permission_granted"
        ):
            return self._blocked(
                reason=(
                    "execution_permission_status_required"
                )
            )

        permission_id = permission_result.get(
            "permission_id"
        )

        if (
            permission_id is None
            or not str(permission_id).strip()
        ):
            return self._blocked(
                reason="permission_id_required"
            )

        approval_id = permission_result.get(
            "approval_id"
        )

        if (
            approval_id is None
            or not str(approval_id).strip()
        ):
            return self._blocked(
                reason="approval_id_required"
            )

        permitted_amount = float(
            permission_result.get(
                "trade_amount",
                0.0,
            )
        )

        starting_value = float(
            starting_value
        )

        if permitted_amount <= 0:
            return self._blocked(
                reason="invalid_permitted_trade_amount"
            )

        if starting_value <= 0:
            raise ValueError(
                "starting_value must be positive"
            )

        if permitted_amount != starting_value:
            return self._blocked(
                reason=(
                    "permitted_trade_amount_mismatch"
                )
            )

        route_id = str(
            route.get(
                "route_id",
                "",
            )
        ).strip()

        if not route_id:
            raise ValueError(
                "route_id is required"
            )

        result = self._orchestrator.execute(
            execution_id=execution_id,
            route=route,
            portfolio=portfolio,
            asset=asset,
            additional_exposure=(
                additional_exposure
            ),
            starting_value=starting_value,
        )

        if result.get(
            "approved"
        ) is not True:
            record = {
                "executed": False,
                "paper_only": True,
                "reason": result.get(
                    "reason"
                ),
                "route_id": route_id,
                "approval_id": approval_id,
                "permission_id": permission_id,
                "trade_amount": starting_value,
                "orchestration_result": result,
                "test_trade": True,
                "simulated": True,
                "paper_trade": True,
                "live_order_submitted": False,
            }

            self._history.append(
                dict(record)
            )

            return dict(record)

        execution = result.get(
            "execution"
        )

        if execution is None:
            return self._blocked(
                reason="paper_execution_required"
            )

        if (
            execution.get("status")
            != "COMPLETED"
        ):
            return self._blocked(
                reason="paper_route_not_completed"
            )

        record = {
            "executed": True,
            "paper_only": True,
            "reason": (
                "live_paper_repeat_scale_cycle_completed"
            ),
            "route_id": route_id,
            "approval_id": approval_id,
            "permission_id": permission_id,
            "trade_amount": starting_value,
            "status": execution.get(
                "status"
            ),
            "final_value": execution.get(
                "final_value"
            ),
            "legs": execution.get(
                "legs",
                [],
            ),
            "reservation_released": (
                result.get(
                    "reservation_released"
                )
            ),
            "orchestration_result": result,
            "test_trade": True,
            "simulated": True,
            "paper_trade": True,
            "live_order_submitted": False,
        }

        self._history.append(
            dict(record)
        )

        return dict(record)

    def history(self):
        return [
            dict(record)
            for record in self._history
        ]

    def total_reserved(self):
        return (
            self._orchestrator.total_reserved()
        )

    @staticmethod
    def _blocked(reason):
        return {
            "executed": False,
            "paper_only": True,
            "reason": reason,
            "test_trade": True,
            "simulated": True,
            "paper_trade": True,
            "live_order_submitted": False,
        }
