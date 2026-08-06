import pytest

from core.live_paper_trading_integration_service import (
    LivePaperTradingIntegrationService,
)


class FakeFreshnessGuard:
    def __init__(self):
        self.fresh = True

    def evaluate(self, symbol, timestamp):
        return {
            "symbol": symbol,
            "fresh": self.fresh,
            "reason": None if self.fresh else "market_data_stale",
        }


class FakeIntakeService:
    def __init__(self):
        self.submitted = []

    def submit(self, opportunity):
        self.submitted.append(dict(opportunity))
        return {
            "accepted": True,
            "queued": True,
            "opportunity_id": opportunity["opportunity_id"],
        }


class FakeTradingService:
    def __init__(self):
        self.run_count = 0

    def run(self):
        self.run_count += 1
        return {
            "processed": 1,
            "completed": 1,
            "rejected": 0,
            "running": False,
        }


@pytest.fixture
def integration_service():
    freshness = FakeFreshnessGuard()
    intake = FakeIntakeService()
    trading = FakeTradingService()

    service = LivePaperTradingIntegrationService(
        freshness_guard=freshness,
        intake_service=intake,
        trading_service=trading,
    )

    return {
        "service": service,
        "freshness": freshness,
        "intake": intake,
        "trading": trading,
    }


def test_rejects_stale_opportunity_before_intake(integration_service):
    service = integration_service["service"]
    freshness = integration_service["freshness"]
    intake = integration_service["intake"]
    trading = integration_service["trading"]

    freshness.fresh = False

    result = service.process({
        "opportunity_id": "OPP-002",
        "symbol": "BTC/USDT",
        "timestamp": 900.0,
        "priority": 10,
        "route": {"route_id": "ROUTE-002"},
    })

    assert result["accepted"] is False
    assert result["fresh"] is False
    assert result["reason"] == "market_data_stale"
    assert intake.submitted == []
    assert trading.run_count == 0


def test_missing_opportunity_is_rejected(integration_service):
    service = integration_service["service"]

    with pytest.raises(ValueError, match="opportunity is required"):
        service.process(None)


def test_missing_symbol_is_rejected(integration_service):
    service = integration_service["service"]

    with pytest.raises(ValueError, match="symbol is required"):
        service.process({
            "opportunity_id": "OPP-003",
            "timestamp": 1000.0,
            "route": {"route_id": "ROUTE-003"},
        })
