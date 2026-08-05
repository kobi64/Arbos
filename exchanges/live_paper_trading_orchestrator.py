"""
ArbOS™
EX-100
Live Paper Trading Orchestrator
"""

from exchanges.portfolio_exposure_concurrent_risk import (
    PortfolioExposureConcurrentRisk,
)
from exchanges.capital_reservation_manager import (
    CapitalReservationManager,
)
from exchanges.multi_leg_atomic_market_snapshot import (
    MultiLegAtomicMarketSnapshot,
)
from exchanges.atomic_multi_leg_paper_execution import (
    AtomicMultiLegPaperExecution,
)


class LivePaperTradingOrchestrator:
    def __init__(self, snapshot_engine):
        self._risk = PortfolioExposureConcurrentRisk()
        self._reservations = CapitalReservationManager()
        self._snapshots = MultiLegAtomicMarketSnapshot(snapshot_engine)
        self._executor = AtomicMultiLegPaperExecution()

    def execute(
        self,
        execution_id,
        route,
        portfolio,
        asset,
        additional_exposure,
        starting_value,
    ):
        if execution_id is None or not str(execution_id).strip():
            raise ValueError("execution_id is required")

        if route is None:
            raise ValueError("route is required")

        risk = self._risk.evaluate(
            portfolio=portfolio,
            asset=asset,
            additional_exposure=additional_exposure,
            required_capital=starting_value,
        )

        if not risk["approved"]:
            return {
                "approved": False,
                "reason": risk["reason"],
                "execution": None,
            }

        reservation = self._reservations.reserve(
            reservation_id=str(execution_id).strip(),
            amount=starting_value,
            available_capital=risk["available_capital"],
        )

        if not reservation["reserved"]:
            return {
                "approved": False,
                "reason": reservation["reason"],
                "execution": None,
            }

        snapshot = self._snapshots.capture(route)

        execution = self._executor.execute(
            route=route,
            atomic_snapshot=snapshot,
            starting_value=starting_value,
        )

        self._reservations.release(str(execution_id).strip())

        return {
            "approved": True,
            "status": execution["status"],
            "execution": execution,
            "reservation_released": True,
        }

    def total_reserved(self):
        return self._reservations.total_reserved()
