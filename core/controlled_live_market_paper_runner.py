"""
ArbOS™
EX-114
Controlled Live Market Paper Runner
"""

from exchanges.ccxt_live_market_data_provider import (
    CCXTLiveMarketDataProvider,
)
from exchanges.auto_valued_safe_live_paper_pipeline import (
    AutoValuedSafeLivePaperPipeline,
)


class ControlledLiveMarketPaperRunner:
    def __init__(self, exchange):
        self._provider = CCXTLiveMarketDataProvider(exchange)
        self._pipeline = AutoValuedSafeLivePaperPipeline(
            self._provider
        )

    def run(
        self,
        opportunity,
        starting_value,
        trading_fees,
        transfer_fees,
        other_costs,
        minimum_profit_percent,
    ):
        if opportunity is None:
            raise ValueError("opportunity is required")

        result = self._pipeline.execute(
            opportunity=opportunity,
            starting_value=starting_value,
            trading_fees=trading_fees,
            transfer_fees=transfer_fees,
            other_costs=other_costs,
            minimum_profit_percent=minimum_profit_percent,
        )

        live_order_submitted = False

        execution = result.get("execution")
        if execution is not None:
            for leg in execution.get("legs", []):
                if leg.get("live_order_submitted"):
                    live_order_submitted = True

        record = dict(result)
        record["paper_only"] = True
        record["live_order_submitted"] = live_order_submitted
        return record
