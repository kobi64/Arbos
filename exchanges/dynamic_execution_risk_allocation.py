"""
ArbOS™
EX-038
Dynamic Execution Risk Allocation Engine

Determines appropriate capital allocation
based on:
- Available capital
- Route reliability
- Risk level

Supports:
- Initial validation trade
- Scale-up approval
- Allocation history
"""

from datetime import datetime, UTC


class DynamicExecutionRiskAllocation:

    def __init__(self):
        self._history = [
            {
                "action": "allocator_created",
                "timestamp": datetime.now(UTC).isoformat(),
            }
        ]

    def calculate_allocation(
        self,
        capital: float,
        reliability: float,
        risk_level: str,
    ):

        if capital <= 0:
            raise ValueError("capital must be positive")

        # ArbOS™ staged execution rule:
        # Always start with controlled validation trade.
        test_trade = min(
            250,
            capital * 0.05,
        )

        if risk_level == "low" and reliability >= 90:
            multiplier = 0.25

        elif risk_level == "medium":
            multiplier = 0.15

        else:
            multiplier = 0.05

        # Reliability adjustment
        reliability_factor = reliability / 100

        maximum_trade = round(
            capital
            * multiplier
            * reliability_factor,
            2,
        )

        result = {
            "test_trade": round(test_trade, 2),
            "maximum_trade": maximum_trade,
            "reason": (
                "Allocation based on capital, "
                "route reliability and risk level"
            ),
        }

        self._history.append(
            {
                "action": "allocation_calculated",
                **result,
                "timestamp": datetime.now(UTC).isoformat(),
            }
        )

        return result

    def validate_execution(
        self,
        test_trade_success: bool,
    ):

        if test_trade_success:

            result = {
                "approved": True,
                "reason": (
                    "Validation trade successful. "
                    "Scaling permitted."
                ),
            }

        else:

            result = {
                "approved": False,
                "reason": (
                    "Validation trade failed. "
                    "Scaling blocked."
                ),
            }

        self._history.append(
            {
                "action": "validation_completed",
                **result,
                "timestamp": datetime.now(UTC).isoformat(),
            }
        )

        return result

    def get_history(self):

        return self._history
