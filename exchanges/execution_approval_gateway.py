"""
ArbOS™
EX-039
Execution Approval Gateway

Provides the final human control checkpoint
before trade execution.
"""

import math
from datetime import datetime, UTC


class ExecutionApprovalGateway:

    def __init__(self):
        self._history = [
            {
                "action": "gateway_created",
                "timestamp": datetime.now(UTC).isoformat(),
            }
        ]
        self._proposals = {}
        self._proposal_sequence = 0

    def create_proposal(
        self,
        route,
        amount,
        expected_profit,
        fees,
        risk,
    ):

        amount = self._finite_number(
            amount,
            "amount",
            positive=True,
        )
        expected_profit = self._finite_number(
            expected_profit,
            "expected_profit",
        )
        fees = self._finite_number(
            fees,
            "fees",
            non_negative=True,
        )

        net_profit = expected_profit - fees

        if net_profit <= 0:
            raise ValueError(
                "net_profit must be positive"
            )

        self._proposal_sequence += 1
        proposal_id = (
            f"TRADE-{self._proposal_sequence:06d}"
        )

        proposal = {
            "proposal_id": proposal_id,
            "route": route,
            "amount": amount,
            "expected_profit": expected_profit,
            "fees": fees,
            "net_profit": round(
                net_profit,
                2,
            ),
            "risk": risk,
            "status": "pending",
        }

        self._proposals[proposal_id] = dict(
            proposal
        )

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

        proposal = self._proposals.get(
            proposal_id
        )

        if proposal is None:
            return {
                "proposal_id": proposal_id,
                "approved": False,
                "status": "not_found",
            }

        if proposal["status"] != "pending":
            return {
                "proposal_id": proposal_id,
                "approved": False,
                "status": "not_pending",
            }

        proposal["status"] = "approved"

        result = {
            "proposal_id": proposal_id,
            "approved": True,
            "status": "approved",
            "proposal": dict(proposal),
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

        proposal = self._proposals.get(
            proposal_id
        )

        if proposal is None:
            return {
                "proposal_id": proposal_id,
                "approved": False,
                "status": "not_found",
            }

        if proposal["status"] != "pending":
            return {
                "proposal_id": proposal_id,
                "approved": False,
                "status": "not_pending",
            }

        proposal["status"] = "rejected"
        proposal["rejection_reason"] = reason

        result = {
            "proposal_id": proposal_id,
            "approved": False,
            "status": "rejected",
            "reason": reason,
            "proposal": dict(proposal),
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

        new_amount = self._finite_number(
            new_amount,
            "new_amount",
            positive=True,
        )

        proposal = self._proposals.get(
            proposal_id
        )

        if proposal is None:
            return {
                "proposal_id": proposal_id,
                "status": "not_found",
            }

        if proposal["status"] != "pending":
            return {
                "proposal_id": proposal_id,
                "status": "not_pending",
            }

        proposal["amount"] = new_amount

        result = {
            "proposal_id": proposal_id,
            "amount": new_amount,
            "status": "modified",
            "proposal": dict(proposal),
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

    @staticmethod
    def _finite_number(
        value,
        field,
        *,
        positive=False,
        non_negative=False,
    ):
        if positive:
            requirement = "positive finite number"
        elif non_negative:
            requirement = "finite non-negative number"
        else:
            requirement = "finite number"

        if isinstance(value, bool):
            raise ValueError(
                f"{field} must be a {requirement}"
            )

        try:
            number = float(value)
        except (
            TypeError,
            ValueError,
            OverflowError,
        ):
            raise ValueError(
                f"{field} must be a {requirement}"
            ) from None

        if not math.isfinite(number):
            raise ValueError(
                f"{field} must be a {requirement}"
            )

        if positive and number <= 0:
            raise ValueError(
                f"{field} must be a {requirement}"
            )

        if non_negative and number < 0:
            raise ValueError(
                f"{field} must be a {requirement}"
            )

        return number
