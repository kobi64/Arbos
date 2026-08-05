"""
ArbOS™
EX-101
Continuous Live Paper Trading Service
"""


class ContinuousLivePaperTradingService:
    def __init__(self, scheduler):
        if scheduler is None:
            raise ValueError("scheduler is required")

        self._scheduler = scheduler
        self._running = False
        self._history = []

    def start(self):
        self._running = True
        return {"started": True}

    def stop(self):
        self._running = False
        return {"stopped": True}

    def is_running(self):
        return self._running

    def run(self):
        self.start()
        processed = 0
        completed = 0
        rejected = 0

        while self._running and self._scheduler.pending_count() > 0:
            result = self._scheduler.process_next()

            if result is None:
                break

            self._history.append(dict(result))
            processed += 1

            if result.get("status") == "COMPLETED":
                completed += 1
            elif result.get("status") == "REJECTED":
                rejected += 1

        self.stop()

        return {
            "processed": processed,
            "completed": completed,
            "rejected": rejected,
            "running": self._running,
        }

    def history(self):
        return [dict(record) for record in self._history]
