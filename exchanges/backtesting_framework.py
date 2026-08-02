"""
ArbOS™
EX-042
Backtesting Framework

Replays simulated trade outcomes
to evaluate historical performance.
"""


class BacktestingFramework:

    def __init__(self):
        self._history = []

    def add_trade(
        self,
        profit,
        success,
    ):

        trade = {
            "profit": profit,
            "success": success,
        }

        self._history.append(trade)

        return trade

    def get_summary(self):

        total_trades = len(self._history)

        if total_trades == 0:
            return {
                "total_trades": 0,
                "successful_trades": 0,
                "failed_trades": 0,
                "total_profit": 0,
            }

        successful_trades = sum(
            1
            for trade in self._history
            if trade["success"]
        )

        failed_trades = total_trades - successful_trades

        total_profit = sum(
            trade["profit"]
            for trade in self._history
        )

        return {
            "total_trades": total_trades,
            "successful_trades": successful_trades,
            "failed_trades": failed_trades,
            "total_profit": total_profit,
        }

    def get_history(self):

        return self._history
