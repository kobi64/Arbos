"""
ArbOS™
EX-041
Simulation Performance Analytics

Analyses simulated trade outcomes
and produces performance metrics.
"""


class SimulationPerformanceAnalytics:

    def __init__(self):
        self._history = []

    def record_result(
        self,
        profit,
        success,
    ):

        result = {
            "profit": profit,
            "success": success,
        }

        self._history.append(result)

        return result

    def get_summary(self):

        total_trades = len(self._history)

        if total_trades == 0:
            return {
                "total_trades": 0,
                "successful_trades": 0,
                "failed_trades": 0,
                "win_rate": 0,
                "average_profit": 0,
            }

        successful_trades = sum(
            1 for trade in self._history
            if trade["success"]
        )

        failed_trades = total_trades - successful_trades

        win_rate = round(
            (successful_trades / total_trades) * 100,
            2,
        )

        average_profit = round(
            sum(
                trade["profit"]
                for trade in self._history
            ) / total_trades,
            2,
        )

        return {
            "total_trades": total_trades,
            "successful_trades": successful_trades,
            "failed_trades": failed_trades,
            "win_rate": win_rate,
            "average_profit": average_profit,
        }

    def get_history(self):

        return self._history
