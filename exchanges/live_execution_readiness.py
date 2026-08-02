"""
ArbOS™
EX-043
Live Execution Readiness

Final safety gate before live execution.
"""


class LiveExecutionReadiness:

    def __init__(self):
        self.simulation_passed = False
        self.risk_passed = False
        self.balance_available = False
        self.approval_granted = False

        self._history = []

    def set_simulation_passed(self, value):
        self.simulation_passed = value

    def set_risk_passed(self, value):
        self.risk_passed = value

    def set_balance_available(self, value):
        self.balance_available = value

    def set_approval_granted(self, value):
        self.approval_granted = value

    def check(self):

        if not self.simulation_passed:
            result = {
                "ready": False,
                "reason": "simulation_not_passed",
            }

        elif not self.risk_passed:
            result = {
                "ready": False,
                "reason": "risk_check_failed",
            }

        elif not self.balance_available:
            result = {
                "ready": False,
                "reason": "insufficient_balance",
            }

        elif not self.approval_granted:
            result = {
                "ready": False,
                "reason": "approval_required",
            }

        else:
            result = {
                "ready": True,
                "reason": "execution_ready",
            }

        self._history.append(result)

        return result

    def reset(self):

        self.simulation_passed = False
        self.risk_passed = False
        self.balance_available = False
        self.approval_granted = False

    def get_history(self):

        return self._history
