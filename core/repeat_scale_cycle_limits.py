"""
ArbOS™
EX-169
Repeat / Scale Cycle Limits

Hard-stop policy for staged repeat/scale cycles.

Adds cycle-specific controls before another EX-168 cycle may
begin while respecting existing circuit-breaker and portfolio
risk decisions.

This module does not approve trades, grant execution permission,
or submit orders.
"""


class RepeatScaleCycleLimits:
    def evaluate(
        self,
        repeat_count,
        scale_count,
        cumulative_trade_amount,
        next_trade_amount,
        max_repeats,
        max_scale_steps,
        max_cumulative_trade_amount,
        circuit_breaker_result,
        portfolio_risk_result,
    ):
        repeat_count = int(repeat_count)
        scale_count = int(scale_count)
        cumulative_trade_amount = float(
            cumulative_trade_amount
        )
        next_trade_amount = float(
            next_trade_amount
        )
        max_repeats = int(max_repeats)
        max_scale_steps = int(max_scale_steps)
        max_cumulative_trade_amount = float(
            max_cumulative_trade_amount
        )

        if repeat_count < 0:
            raise ValueError(
                "repeat_count cannot be negative"
            )

        if scale_count < 0:
            raise ValueError(
                "scale_count cannot be negative"
            )

        if cumulative_trade_amount < 0:
            raise ValueError(
                "cumulative_trade_amount cannot be negative"
            )

        if next_trade_amount <= 0:
            raise ValueError(
                "next_trade_amount must be positive"
            )

        if max_repeats < 0:
            raise ValueError(
                "max_repeats cannot be negative"
            )

        if max_scale_steps < 0:
            raise ValueError(
                "max_scale_steps cannot be negative"
            )

        if max_cumulative_trade_amount <= 0:
            raise ValueError(
                "max_cumulative_trade_amount must be positive"
            )

        if circuit_breaker_result is None:
            raise ValueError(
                "circuit_breaker_result is required"
            )

        if portfolio_risk_result is None:
            raise ValueError(
                "portfolio_risk_result is required"
            )

        if (
            circuit_breaker_result.get("allowed")
            is not True
        ):
            return self._blocked(
                reason="execution_circuit_open",
                repeat_count=repeat_count,
                scale_count=scale_count,
                cumulative_trade_amount=(
                    cumulative_trade_amount
                ),
                next_trade_amount=next_trade_amount,
            )

        if (
            portfolio_risk_result.get("approved")
            is not True
        ):
            return self._blocked(
                reason=portfolio_risk_result.get(
                    "reason",
                    "portfolio_risk_rejected",
                ),
                repeat_count=repeat_count,
                scale_count=scale_count,
                cumulative_trade_amount=(
                    cumulative_trade_amount
                ),
                next_trade_amount=next_trade_amount,
            )

        if repeat_count >= max_repeats:
            return self._blocked(
                reason="maximum_repeat_count_reached",
                repeat_count=repeat_count,
                scale_count=scale_count,
                cumulative_trade_amount=(
                    cumulative_trade_amount
                ),
                next_trade_amount=next_trade_amount,
            )

        if scale_count >= max_scale_steps:
            scale_allowed = False
        else:
            scale_allowed = True

        projected_cumulative_amount = (
            cumulative_trade_amount
            + next_trade_amount
        )

        if (
            projected_cumulative_amount
            > max_cumulative_trade_amount
        ):
            return self._blocked(
                reason=(
                    "maximum_cumulative_trade_amount_exceeded"
                ),
                repeat_count=repeat_count,
                scale_count=scale_count,
                cumulative_trade_amount=(
                    cumulative_trade_amount
                ),
                next_trade_amount=next_trade_amount,
                projected_cumulative_amount=(
                    projected_cumulative_amount
                ),
            )

        return {
            "allowed": True,
            "hard_stop": False,
            "reason": None,
            "repeat_count": repeat_count,
            "scale_count": scale_count,
            "next_repeat_count": repeat_count + 1,
            "scale_allowed": scale_allowed,
            "cumulative_trade_amount": (
                cumulative_trade_amount
            ),
            "next_trade_amount": next_trade_amount,
            "projected_cumulative_trade_amount": (
                projected_cumulative_amount
            ),
            "max_repeats": max_repeats,
            "max_scale_steps": max_scale_steps,
            "max_cumulative_trade_amount": (
                max_cumulative_trade_amount
            ),
            "live_order_submitted": False,
        }

    def evaluate_scale(
        self,
        limit_result,
    ):
        if limit_result is None:
            raise ValueError(
                "limit_result is required"
            )

        if limit_result.get("allowed") is not True:
            return {
                "scale_allowed": False,
                "reason": "cycle_not_allowed",
                "live_order_submitted": False,
            }

        if limit_result.get("scale_allowed") is not True:
            return {
                "scale_allowed": False,
                "reason": "maximum_scale_steps_reached",
                "live_order_submitted": False,
            }

        return {
            "scale_allowed": True,
            "reason": None,
            "live_order_submitted": False,
        }

    @staticmethod
    def _blocked(
        reason,
        repeat_count,
        scale_count,
        cumulative_trade_amount,
        next_trade_amount,
        projected_cumulative_amount=None,
    ):
        if projected_cumulative_amount is None:
            projected_cumulative_amount = (
                cumulative_trade_amount
                + next_trade_amount
            )

        return {
            "allowed": False,
            "hard_stop": True,
            "reason": reason,
            "repeat_count": repeat_count,
            "scale_count": scale_count,
            "next_repeat_count": repeat_count,
            "scale_allowed": False,
            "cumulative_trade_amount": (
                cumulative_trade_amount
            ),
            "next_trade_amount": next_trade_amount,
            "projected_cumulative_trade_amount": (
                projected_cumulative_amount
            ),
            "live_order_submitted": False,
        }
