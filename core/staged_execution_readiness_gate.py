"""
ArbOS™
EX-150
Staged Execution Readiness Gate

Determines whether a profitable, paper-verified route
is eligible to proceed to the staged execution workflow.

This gate does not submit live orders.
"""

import math

from exchanges.exchange_execution_safety_gate import (
    ExchangeExecutionSafetyGate,
)


class StagedExecutionReadinessGate:
    def __init__(self):
        self._safety_gate = ExchangeExecutionSafetyGate()

    def evaluate(
        self,
        scan_result,
        safety_context,
    ):
        if scan_result is None:
            raise ValueError(
                "scan_result is required"
            )

        if safety_context is None:
            raise ValueError(
                "safety_context is required"
            )

        if scan_result.get("paper_only") is not True:
            return {
                "ready_for_staged_execution": False,
                "reason": "paper_verification_required",
                "route": None,
                "live_order_submitted": bool(
                    scan_result.get(
                        "live_order_submitted",
                        False,
                    )
                ),
            }

        if scan_result.get(
            "live_order_submitted"
        ) is True:
            return {
                "ready_for_staged_execution": False,
                "reason": "live_order_already_submitted",
                "route": None,
                "live_order_submitted": True,
            }

        route = scan_result.get(
            "best_profitable_route"
        )

        if route is None:
            return {
                "ready_for_staged_execution": False,
                "reason": "no_profitable_route",
                "route": None,
                "live_order_submitted": False,
            }

        if route.get("executable") is not True:
            return {
                "ready_for_staged_execution": False,
                "reason": "route_not_executable",
                "route": route,
                "live_order_submitted": False,
            }

        profitability = {}

        for field in (
            "net_profit",
            "net_profit_percent",
        ):
            value = route.get(field)

            if isinstance(value, bool):
                return {
                    "ready_for_staged_execution": False,
                    "reason": "invalid_route_profitability",
                    "route": route,
                    "live_order_submitted": False,
                }

            try:
                number = float(value)
            except (
                TypeError,
                ValueError,
                OverflowError,
            ):
                return {
                    "ready_for_staged_execution": False,
                    "reason": "invalid_route_profitability",
                    "route": route,
                    "live_order_submitted": False,
                }

            if (
                not math.isfinite(number)
                or number <= 0
            ):
                return {
                    "ready_for_staged_execution": False,
                    "reason": "invalid_route_profitability",
                    "route": route,
                    "live_order_submitted": False,
                }

            profitability[field] = number

        safety = self._safety_gate.evaluate(
            safety_context
        )

        if not safety["allowed"]:
            return {
                "ready_for_staged_execution": False,
                "reason": "execution_safety_failed",
                "reasons": safety["reasons"],
                "route": route,
                "live_order_submitted": False,
            }

        return {
            "ready_for_staged_execution": True,
            "reason": "ready_for_staged_execution",
            "reasons": [],
            "route": route,
            "live_order_submitted": False,
        }
