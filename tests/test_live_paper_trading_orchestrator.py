import pytest

from exchanges.live_paper_trading_orchestrator import (
    LivePaperTradingOrchestrator,
)


class FakeSnapshotEngine:
    def __init__(self):
        self.timestamp = 1000

    def snapshot(self, symbol, limit=None):
        self.timestamp += 1
        books = {
            "BTC/USDT": {
                "bids": [[61900.0, 10.0]],
                "asks": [[62000.0, 10.0]],
            },
            "ETH/BTC": {
                "bids": [[0.049, 100.0]],
                "asks": [[0.05, 100.0]],
            },
            "ETH/USDT": {
                "bids": [[3200.0, 100.0]],
                "asks": [[3210.0, 100.0]],
            },
        }
        book = books[symbol]
        return {
            "symbol": symbol,
            "bids": book["bids"],
            "asks": book["asks"],
            "timestamp": self.timestamp,
        }


@pytest.fixture
def orchestrator():
    return LivePaperTradingOrchestrator(FakeSnapshotEngine())


def valid_route():
    return {
        "route_id": "ROUTE-001",
        "legs": [
            {"symbol": "BTC/USDT", "side": "buy"},
            {"symbol": "ETH/BTC", "side": "buy"},
            {"symbol": "ETH/USDT", "side": "sell"},
        ],
    }


def safe_portfolio():
    return {
        "total_capital": 1000.0,
        "reserved_capital": 0.0,
        "asset_exposure": {"BTC": 0.10},
        "max_asset_exposure": 0.25,
        "open_routes": 0,
        "max_open_routes": 3,
    }


def test_executes_safe_live_paper_route(orchestrator):
    result = orchestrator.execute(
        execution_id="EXEC-001",
        route=valid_route(),
        portfolio=safe_portfolio(),
        asset="BTC",
        additional_exposure=0.05,
        starting_value=100.0,
    )

    assert result["approved"] is True
    assert result["status"] == "COMPLETED"
    assert result["execution"]["route_id"] == "ROUTE-001"
    assert result["reservation_released"] is True


def test_rejects_route_when_portfolio_risk_fails(orchestrator):
    portfolio = safe_portfolio()
    portfolio["asset_exposure"]["BTC"] = 0.24

    result = orchestrator.execute(
        execution_id="EXEC-002",
        route=valid_route(),
        portfolio=portfolio,
        asset="BTC",
        additional_exposure=0.05,
        starting_value=100.0,
    )

    assert result["approved"] is False
    assert result["reason"] == "asset_exposure_exceeded"
    assert result["execution"] is None


def test_releases_capital_after_successful_execution(orchestrator):
    orchestrator.execute(
        execution_id="EXEC-003",
        route=valid_route(),
        portfolio=safe_portfolio(),
        asset="BTC",
        additional_exposure=0.05,
        starting_value=100.0,
    )

    assert orchestrator.total_reserved() == 0.0


def test_missing_execution_id_is_rejected(orchestrator):
    with pytest.raises(ValueError, match="execution_id is required"):
        orchestrator.execute(
            execution_id="",
            route=valid_route(),
            portfolio=safe_portfolio(),
            asset="BTC",
            additional_exposure=0.05,
            starting_value=100.0,
        )


def test_missing_route_is_rejected(orchestrator):
    with pytest.raises(ValueError, match="route is required"):
        orchestrator.execute(
            execution_id="EXEC-004",
            route=None,
            portfolio=safe_portfolio(),
            asset="BTC",
            additional_exposure=0.05,
            starting_value=100.0,
        )
