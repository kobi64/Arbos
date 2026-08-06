"""
ArbOS™
EX-113
Live Paper Trading Integration Service
"""


class LivePaperTradingIntegrationService:
    def __init__(
        self,
        freshness_guard,
        intake_service,
        trading_service,
    ):
        self._freshness = freshness_guard
        self._intake = intake_service
        self._trading = trading_service

    def process(self, opportunity):
        if opportunity is None:
            raise ValueError("opportunity is required")

        symbol = opportunity.get("symbol")
        if symbol is None or not str(symbol).strip():
            raise ValueError("symbol is required")

        freshness = self._freshness.evaluate(
            symbol=symbol,
            timestamp=opportunity.get("timestamp"),
        )

        if not freshness["fresh"]:
            return {
                "accepted": False,
                "fresh": False,
                "queued": False,
                "reason": freshness["reason"],
                "processed": 0,
                "completed": 0,
            }

        intake = self._intake.submit(opportunity)
        trading = self._trading.run()

        return {
            "accepted": intake["accepted"],
            "fresh": True,
            "queued": intake["queued"],
            "reason": None,
            "processed": trading["processed"],
            "completed": trading["completed"],
            "rejected": trading.get("rejected", 0),
        }
