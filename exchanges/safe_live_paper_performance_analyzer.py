"""
ArbOS™
EX-085
Safe Live Paper Performance Analyzer
"""


class SafeLivePaperPerformanceAnalyzer:
    def __init__(self):
        self._history = []

    def analyze(self, replay_records):
        if replay_records is None:
            raise ValueError("replay_records are required")

        if not isinstance(replay_records, list):
            raise ValueError("replay_records must be a list")

        total_records = len(replay_records)

        completed = 0
        failed = 0
        rejected = 0
        total_profit = 0.0

        for record in replay_records:
            execution = record.get("execution") or {}

            status = execution.get("status")

            if status == "COMPLETED":
                completed += 1

            elif status == "FAILED":
                failed += 1

            elif status == "REJECTED":
                rejected += 1

            pnl = record.get("pnl") or {}

            profit = pnl.get("profit")

            if isinstance(profit, (int, float)):
                total_profit += profit

        result = {
            "total_records": total_records,
            "completed": completed,
            "failed": failed,
            "rejected": rejected,
            "total_profit": round(total_profit, 2),
            "average_profit": (
                round(total_profit / completed, 2)
                if completed
                else 0
            ),
        }

        self._history.append(dict(result))

        return dict(result)

    def history(self):
        return [dict(record) for record in self._history]
