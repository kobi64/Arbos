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


@pytest.mark.parametrize(
    "required_capital",
    [
        None,
        "not-a-number",
        float("nan"),
        float("inf"),
        float("-inf"),
        True,
    ],
)
def test_invalid_required_capital_numeric_contract(
    engine,
    required_capital,
):
    with pytest.raises(
        ValueError,
        match="required_capital must be a finite positive number",
    ):
        engine.evaluate(
            portfolio=sample_portfolio(),
            asset="BTC",
            additional_exposure=0.01,
            required_capital=required_capital,
        )


@pytest.mark.parametrize(
    "field,value",
    [
        ("total_capital", None),
        ("total_capital", "bad"),
        ("total_capital", float("nan")),
        ("total_capital", float("inf")),
        ("total_capital", float("-inf")),
        ("total_capital", True),
        ("reserved_capital", None),
        ("reserved_capital", "bad"),
        ("reserved_capital", float("nan")),
        ("reserved_capital", float("inf")),
        ("reserved_capital", float("-inf")),
        ("reserved_capital", True),
        ("max_asset_exposure", None),
        ("max_asset_exposure", "bad"),
        ("max_asset_exposure", float("nan")),
        ("max_asset_exposure", float("inf")),
        ("max_asset_exposure", float("-inf")),
        ("max_asset_exposure", True),
    ],
)
def test_invalid_portfolio_numeric_fields_are_rejected(
    engine,
    field,
    value,
):
    portfolio = sample_portfolio()
    portfolio[field] = value

    with pytest.raises(ValueError):
        engine.evaluate(
            portfolio=portfolio,
            asset="BTC",
            additional_exposure=0.01,
            required_capital=100.0,
        )


@pytest.mark.parametrize(
    "additional_exposure",
    [
        None,
        "not-a-number",
        float("nan"),
        float("inf"),
        float("-inf"),
        True,
    ],
)
def test_invalid_additional_exposure_is_rejected(
    engine,
    additional_exposure,
):
    with pytest.raises(
        ValueError,
        match="additional_exposure must be a finite non-negative number",
    ):
        engine.evaluate(
            portfolio=sample_portfolio(),
            asset="BTC",
            additional_exposure=additional_exposure,
            required_capital=100.0,
        )


@pytest.mark.parametrize(
    "field",
    [
        "total_capital",
        "reserved_capital",
        "max_asset_exposure",
        "open_routes",
    ],
)
def test_required_portfolio_risk_fields_are_not_silently_defaulted(
    engine,
    field,
):
    portfolio = sample_portfolio()
    del portfolio[field]

    with pytest.raises(ValueError):
        engine.evaluate(
            portfolio=portfolio,
            asset="BTC",
            additional_exposure=0.01,
            required_capital=100.0,
        )


@pytest.mark.parametrize(
    "value",
    [
        -1,
        1.5,
        "1.5",
        True,
        float("nan"),
        float("inf"),
        float("-inf"),
    ],
)
def test_invalid_open_routes_is_rejected(engine, value):
    portfolio = sample_portfolio()
    portfolio["open_routes"] = value

    with pytest.raises(
        ValueError,
        match="open_routes must be a non-negative integer",
    ):
        engine.evaluate(
            portfolio=portfolio,
            asset="BTC",
            additional_exposure=0.01,
            required_capital=100.0,
        )


def test_reserved_capital_cannot_exceed_total_capital(engine):
    portfolio = sample_portfolio()
    portfolio["total_capital"] = 1000.0
    portfolio["reserved_capital"] = 1001.0

    with pytest.raises(
        ValueError,
        match="reserved_capital cannot exceed total_capital",
    ):
        engine.evaluate(
            portfolio=portfolio,
            asset="BTC",
            additional_exposure=0.01,
            required_capital=100.0,
        )


@pytest.mark.parametrize(
    "current_exposure",
    [
        None,
        "not-a-number",
        float("nan"),
        float("inf"),
        float("-inf"),
        True,
        -0.01,
    ],
)
def test_invalid_current_asset_exposure_is_rejected(
    engine,
    current_exposure,
):
    portfolio = sample_portfolio()
    portfolio["asset_exposure"]["BTC"] = current_exposure

    with pytest.raises(
        ValueError,
        match="current_asset_exposure must be a finite non-negative number",
    ):
        engine.evaluate(
            portfolio=portfolio,
            asset="BTC",
            additional_exposure=0.01,
            required_capital=100.0,
        )
