"""
ArbOS™
EX-069
End-to-End Paper Execution Harness
"""

from exchanges.live_market_paper_bridge import LiveMarketPaperBridge
from exchanges.pre_execution_validation import PreExecutionValidationPipeline


class EndToEndPaperExecutionHarness:
    def __init__(self, market_data_provider):
        self._validator = PreExecutionValidationPipeline()
        self._bridge = LiveMarketPaperBridge(market_data_provider)
        self._history = []

    def execute(self, execution_id, order):
        if execution_id is None or not str(execution_id).strip():
            raise ValueError("execution_id is required")

        if order is None:
            raise ValueError("order is required")

        validation = self._validator.validate(order)

        if not validation["valid"]:
            raise ValueError(",".join(validation["reasons"]))

        result = self._bridge.execute(order)
        result["execution_id"] = str(execution_id).strip()

        self._history.append(dict(result))
        return dict(result)

    def history(self):
        return [dict(record) for record in self._history]
