"""
ArbOS™
EX-060
Order Cancellation & Abort Coordination Engine
"""


class OrderCancellationAbortCoordinator:
    SUPPORTED_STATES = {
        "PENDING",
        "OPEN",
        "PARTIALLY_FILLED",
        "FILLED",
        "CANCELLED",
        "UNKNOWN",
    }

    def evaluate(self, order_state, abort_requested):
        if order_state is None:
            raise ValueError("order_state is required")

        state = str(order_state).strip().upper()

        if state not in self.SUPPORTED_STATES:
            raise ValueError("unsupported order_state")

        if not abort_requested:
            return {
                "action": "NO_ACTION",
                "abort_allowed": False,
                "escalate": False,
                "reconcile_required": False,
            }

        if state == "PENDING":
            return {
                "action": "ABORT_WORKFLOW",
                "abort_allowed": True,
                "escalate": False,
                "reconcile_required": False,
            }

        if state == "OPEN":
            return {
                "action": "CANCEL_ORDER",
                "abort_allowed": True,
                "escalate": False,
                "reconcile_required": False,
            }

        if state == "PARTIALLY_FILLED":
            return {
                "action": "CANCEL_AND_RECONCILE",
                "abort_allowed": True,
                "escalate": False,
                "reconcile_required": True,
            }

        if state == "FILLED":
            return {
                "action": "NO_CANCEL_POSSIBLE",
                "abort_allowed": False,
                "escalate": True,
                "reconcile_required": False,
            }

        if state == "CANCELLED":
            return {
                "action": "ALREADY_CANCELLED",
                "abort_allowed": False,
                "escalate": False,
                "reconcile_required": False,
            }

        return {
            "action": "RECONCILE_BEFORE_ABORT",
            "abort_allowed": False,
            "escalate": True,
            "reconcile_required": True,
        }
