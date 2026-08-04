import pytest

from exchanges.portfolio_exposure_concurrent_risk import (
    PortfolioExposureConcurrentRisk,
)


@pytest.fixture
def engine():
    return PortfolioExposureConcurrentRisk()


def sample_portfolio():
    return {
        "total_capital": 1000.0,
        "reserved_capital": 200.0,
        "asset_exposure": {
            "BTC": 0.18,
            "ETH": 0.07,
            "USDT": 0.50,
        },
        "max_asset_exposure": 0.25,
        "open_routes": 2,
    }


def test_accepts_safe_portfolio(engine):
    result = engine.evaluate(
        portfolio=sample_portfolio(),
        asset="BTC",
        additional_exposure=0.03,
        required_capital=100.0,
    )

    assert result["approved"] is True
    assert result["reason"] is None


def test_rejects_asset_exposure_above_limit(engine):
    result = engine.evaluate(
        portfolio=sample_portfolio(),
        asset="BTC",
        additional_exposure=0.10,
        required_capital=100.0,
    )

    assert result["approved"] is False
    assert result["reason"] == "asset_exposure_exceeded"


def test_rejects_when_available_capital_is_insufficient(engine):
    result = engine.evaluate(
        portfolio=sample_portfolio(),
        asset="ETH",
        additional_exposure=0.02,
        required_capital=850.0,
    )

    assert result["approved"] is False
    assert result["reason"] == "insufficient_unreserved_capital"


def test_rejects_when_open_route_limit_is_reached(engine):
    portfolio = sample_portfolio()
    portfolio["max_open_routes"] = 2

    result = engine.evaluate(
        portfolio=portfolio,
        asset="ETH",
        additional_exposure=0.02,
        required_capital=100.0,
    )

    assert result["approved"] is False
    assert result["reason"] == "concurrent_route_limit_reached"


def test_missing_portfolio_is_rejected(engine):
    with pytest.raises(ValueError, match="portfolio is required"):
        engine.evaluate(
            portfolio=None,
            asset="BTC",
            additional_exposure=0.01,
            required_capital=100.0,
        )


def test_non_positive_required_capital_is_rejected(engine):
    with pytest.raises(ValueError, match="required_capital must be positive"):
        engine.evaluate(
            portfolio=sample_portfolio(),
            asset="BTC",
            additional_exposure=0.01,
            required_capital=0.0,
        )
