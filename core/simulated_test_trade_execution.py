"""
ArbOS™
EX-158
Simulated Test Trade Execution

Executes an accepted staged test-trade order through the
existing live-market paper execution bridge.

This module does not submit live exchange orders.
"""

from exchanges.live_market_paper_bridge import (
    LiveMarketPaperBridge,
)


class SimulatedTestTradeExecution:
    def __init__(
        self,
        market_data_provider,
    ):
        self._bridge = LiveMarketPaperBridge(
            market_data_provider
        )

    def execute(
        self,
        submission_result,
        order_record,
    ):
        if submission_result is None:
            raise ValueError(
                "submission_result is required"
            )

        if order_record is None:
            raise ValueError(
                "order_record is required"
            )

        if submission_result.get(
            "live_order_submitted"
        ) is True:
            return {
                "simulated": False,
                "reason": "live_order_already_submitted",
                "live_order_submitted": True,
            }

        if submission_result.get(
            "accepted"
        ) is not True:
            return {
                "simulated": False,
                "reason": "order_submission_not_accepted",
                "live_order_submitted": False,
            }

        if submission_result.get(
            "test_trade"
        ) is not True:
            return {
                "simulated": False,
                "reason": "test_trade_required",
                "live_order_submitted": False,
            }

        submission_order_id = (
            submission_result.get("order_id")
        )

        record_order_id = (
            order_record.get("order_id")
        )

        if submission_order_id != record_order_id:
            return {
                "simulated": False,
                "reason": "order_id_mismatch",
                "live_order_submitted": False,
            }

        paper_order = {
            "symbol": order_record.get(
                "symbol"
            ),
            "side": str(
                order_record.get(
                    "side",
                    "",
                )
            ).strip().lower(),
            "order_type": "market",
            "quantity": float(
                order_record.get(
                    "amount",
                    0.0,
                )
            ),
        }

        result = self._bridge.execute(
            paper_order
        )

        return {
            **result,
            "simulated": True,
            "order_id": record_order_id,
            "route_id": submission_result.get(
                "route_id"
            ),
            "approval_id": submission_result.get(
                "approval_id"
            ),
            "permission_id": submission_result.get(
                "permission_id"
            ),
            "test_trade": True,
            "live_order_submitted": False,
        }
