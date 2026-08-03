"""
ArbOS™
EX-070
Scanner Paper Execution Coordinator
"""

from exchanges.end_to_end_paper_execution_harness import (
    EndToEndPaperExecutionHarness,
)


class ScannerPaperExecutionCoordinator:
    def __init__(self, market_data_provider):
        self._harness = EndToEndPaperExecutionHarness(market_data_provider)
        self._history = []

    def execute(self, opportunity):
        if opportunity is None:
            raise ValueError("opportunity is required")

        opportunity_id = opportunity.get("opportunity_id")

        if opportunity_id is None or not str(opportunity_id).strip():
            raise ValueError("opportunity_id is required")

        order = {
            "symbol": opportunity.get("symbol"),
            "side": opportunity.get("side"),
            "order_type": opportunity.get("order_type"),
            "quantity": opportunity.get("quantity"),
            "price": None,
        }

        result = self._harness.execute(
            execution_id=str(opportunity_id).strip(),
            order=order,
        )

        result["opportunity_id"] = str(opportunity_id).strip()

        self._history.append(dict(result))
        return dict(result)

    def history(self):
        return [dict(record) for record in self._history]
