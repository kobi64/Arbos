import pytest

from exchanges.live_opportunity_route_builder import (
    LiveOpportunityRouteBuilder,
)


@pytest.fixture
def builder():
    return LiveOpportunityRouteBuilder()


def valid_opportunity():
    return {
        "opportunity_id": "OPP-001",
        "legs": [
            {"symbol": "BTC/USDT", "side": "buy", "quantity": 0.01},
            {"symbol": "ETH/BTC", "side": "buy", "quantity": 0.2},
            {"symbol": "ETH/USDT", "side": "sell", "quantity": 0.2},
        ],
    }


def test_builds_route_from_opportunity(builder):
    result = builder.build(valid_opportunity())

    assert result["route_id"] == "OPP-001"
    assert len(result["legs"]) == 3


def test_leg_details_are_preserved(builder):
    result = builder.build(valid_opportunity())

    assert result["legs"][0]["symbol"] == "BTC/USDT"
    assert result["legs"][0]["side"] == "buy"
    assert result["legs"][0]["quantity"] == 0.01


def test_missing_opportunity_is_rejected(builder):
    with pytest.raises(ValueError, match="opportunity is required"):
        builder.build(None)


def test_missing_opportunity_id_is_rejected(builder):
    opportunity = valid_opportunity()
    del opportunity["opportunity_id"]

    with pytest.raises(ValueError, match="opportunity_id is required"):
        builder.build(opportunity)


def test_missing_legs_is_rejected(builder):
    opportunity = valid_opportunity()
    del opportunity["legs"]

    with pytest.raises(ValueError, match="legs are required"):
        builder.build(opportunity)


def test_empty_legs_are_rejected(builder):
    opportunity = valid_opportunity()
    opportunity["legs"] = []

    with pytest.raises(ValueError, match="legs are required"):
        builder.build(opportunity)


def test_leg_missing_symbol_is_rejected(builder):
    opportunity = valid_opportunity()
    del opportunity["legs"][0]["symbol"]

    with pytest.raises(ValueError, match="leg symbol is required"):
        builder.build(opportunity)
