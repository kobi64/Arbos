"""
ArbOS™
EX-082
Safe Live Paper Orchestrator
"""

from exchanges.safe_live_paper_readiness_gate import (
    SafeLivePaperReadinessGate,
)
from exchanges.safe_live_paper_pipeline import (
    SafeLivePaperPipeline,
)


class SafeLivePaperOrchestrator:
    def __init__(self, market_data_provider):
        self._readiness = SafeLivePaperReadinessGate()
        self._pipeline = SafeLivePaperPipeline(
            market_data_provider
        )
        self._history = []

    def execute(
        self,
        opportunity,
        starting_value,
        gross_final_value,
        trading_fees,
        transfer_fees,
        other_costs,
        minimum_profit_percent,
        exchange_connected,
        account_valid,
        trading_pair_active,
        sufficient_balance,
        gas_available,
        withdrawal_enabled,
        approval_granted,
    ):
        readiness = self._readiness.evaluate(
            opportunity=opportunity,
            exchange_connected=exchange_connected,
            account_valid=account_valid,
            trading_pair_active=trading_pair_active,
            sufficient_balance=sufficient_balance,
            gas_available=gas_available,
            withdrawal_enabled=withdrawal_enabled,
            approval_granted=approval_granted,
        )

        if not readiness["ready"]:
            record = {
                "ready": False,
                "reason": readiness["reason"],
                "execution": None,
            }

            self._history.append(dict(record))
            return dict(record)

        result = self._pipeline.execute(
            opportunity=opportunity,
            starting_value=starting_value,
            gross_final_value=gross_final_value,
            trading_fees=trading_fees,
            transfer_fees=transfer_fees,
            other_costs=other_costs,
            minimum_profit_percent=minimum_profit_percent,
        )

        record = {
            "ready": True,
            "reason": readiness["reason"],
            "result": result,
            "execution": result.get("execution"),
        }

        self._history.append(dict(record))
        return dict(record)

    def history(self):
        return [dict(record) for record in self._history]
