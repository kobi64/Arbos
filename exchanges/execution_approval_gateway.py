"""
ArbOS™
EX-039
Execution Approval Gateway

Provides the final human control checkpoint
before trade execution.
"""

from datetime import datetime, UTC


class ExecutionApprovalGateway:

    def __init__(self):
        self._history = [
            {
                "action": "gateway_created",
                "timestamp": datetime.now(UTC).isoformat(),
            }
        ]

    def create_proposal(
        self,
        route,
        amount,
        expected_profit,
        fees,
        risk,
    ):

        proposal = {
            "route": route,
            "amount": amount,
            "expected_profit": expected_profit,
            "fees": fees,
            "net_profit": round(
                expected_profit - fees,
                2,
            ),
            "risk": risk,
            "status": "pending",
        }

        self._history.append(
            {
                "action": "proposal_created",
                "proposal": proposal,
                "timestamp": datetime.now(UTC).isoformat(),
            }
        )

        return proposal

    def approve(
        self,
        proposal_id,
    ):

        result = {
            "proposal_id": proposal_id,
            "approved": True,
            "status": "approved",
        }

        self._history.append(
            {
                "action": "trade_approved",
                **result,
                "timestamp": datetime.now(UTC).isoformat(),
            }
        )

        return result

    def reject(
        self,
        proposal_id,
        reason,
    ):

        result = {
            "proposal_id": proposal_id,
            "approved": False,
            "status": "rejected",
            "reason": reason,
        }

        self._history.append(
            {
                "action": "trade_rejected",
                **result,
                "timestamp": datetime.now(UTC).isoformat(),
            }
        )

        return result

    def modify(
        self,
        proposal_id,
        new_amount,
    ):

        result = {
            "proposal_id": proposal_id,
            "amount": new_amount,
            "status": "modified",
        }

        self._history.append(
            {
                "action": "trade_modified",
                **result,
                "timestamp": datetime.now(UTC).isoformat(),
            }
        )

        return result

    def get_history(self):

        return self._history
