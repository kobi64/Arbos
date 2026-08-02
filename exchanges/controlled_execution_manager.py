"""
ArbOS™
EX-044
Controlled Execution Manager

Controls the final transition from
approved trade readiness to execution.
"""


class ControlledExecutionManager:

    def __init__(self, max_trade_size=1000):

        self.max_trade_size = max_trade_size

        self.trade_ready = False
        self.approved = False
        self.execution_permission = False
        self.executed = False

        self._history = []

    def set_trade_ready(self, value):
        self.trade_ready = value

    def set_approved(self, value):
        self.approved = value

    def set_execution_permission(self, value):
        self.execution_permission = value

    def execute(self, trade_size=0):

        if self.executed:
            result = {
                "executed": False,
                "reason": "duplicate_execution_blocked",
            }

        elif not self.trade_ready:
            result = {
                "executed": False,
                "reason": "trade_not_ready",
            }

        elif not self.approved:
            result = {
                "executed": False,
                "reason": "approval_required",
            }

        elif not self.execution_permission:
            result = {
                "executed": False,
                "reason": "execution_permission_required",
            }

        elif trade_size > self.max_trade_size:
            result = {
                "executed": False,
                "reason": "trade_size_limit_exceeded",
            }

        else:
            self.executed = True

            result = {
                "executed": True,
                "reason": "execution_authorised",
            }

        self._history.append(result)

        return result

    def get_history(self):

        return self._history
