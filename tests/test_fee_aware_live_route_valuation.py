import pytest

from exchanges.fee_aware_live_route_valuation import (
    FeeAwareLiveRouteValuation,
)


class FakeMarketDataProvider:
    def __init__(self):
        self.prices = {
            "BTC/USDT": {"bid": 61900.0, "ask": 62000.0},
            "ETH/BTC": {"bid": 0.049, "ask": 0.05},
            "ETH/USDT": {"bid": 3200.0, "ask": 3210.0},
        }

    def get_bid(self, symbol):
        return self.prices[symbol]["bid"]

    def get_ask(self, symbol):
        return self.prices[symbol]["ask"]


@pytest.fixture
def valuation():
    return FeeAwareLiveRouteValuation(FakeMarketDataProvider())


def valid_route():
    return {
        "route_id": "ROUTE-001",
        "legs": [
            {"symbol": "BTC/USDT", "side": "buy", "fee_rate": 0.004},
            {"symbol": "ETH/BTC", "side": "buy", "fee_rate": 0.004},
            {"symbol": "ETH/USDT", "side": "sell", "fee_rate": 0.004},
        ],
    }


def test_deducts_fee_after_each_leg(valuation):
    result = valuation.evaluate(
        route=valid_route(),
        starting_value=1000.0,
    )

    leg1 = (1000.0 / 62000.0) * (1.0 - 0.004)
    leg2 = (leg1 / 0.05) * (1.0 - 0.004)
    expected = (leg2 * 3200.0) * (1.0 - 0.004)

    assert result["gross_final_value"] == pytest.approx(expected)
    assert result["total_fee_rate_effect"] > 0


def test_records_fee_details_for_each_leg(valuation):
    result = valuation.evaluate(
        route=valid_route(),
        starting_value=1000.0,
    )

    assert len(result["legs"]) == 3
    assert result["legs"][0]["fee_rate"] == 0.004
    assert result["legs"][0]["fee_amount"] > 0
    assert result["legs"][0]["net_output_amount"] > 0


def test_negative_fee_rate_is_rejected(valuation):
    route = valid_route()
    route["legs"][0]["fee_rate"] = -0.001

    with pytest.raises(ValueError, match="fee_rate must be non-negative"):
        valuation.evaluate(route=route, starting_value=1000.0)


def test_missing_route_is_rejected(valuation):
    with pytest.raises(ValueError, match="route is required"):
        valuation.evaluate(route=None, starting_value=1000.0)


def test_invalid_starting_value_is_rejected(valuation):
    with pytest.raises(ValueError, match="starting_value must be positive"):
        valuation.evaluate(route=valid_route(), starting_value=0.0)


@pytest.mark.parametrize(
    "starting_value",
    [
        None,
        "not-a-number",
        float("nan"),
        float("inf"),
        float("-inf"),
        0.0,
        -1.0,
    ],
)
def test_invalid_numeric_starting_values_are_rejected(
    valuation,
    starting_value,
):
    with pytest.raises(
        ValueError,
        match="starting_value must be positive",
    ):
        valuation.evaluate(
            route=valid_route(),
            starting_value=starting_value,
        )


def test_numeric_string_starting_value_is_normalized(
    valuation,
):
    result = valuation.evaluate(
        route=valid_route(),
        starting_value="1000",
    )

    assert result["starting_value"] == 1000.0
    assert isinstance(result["starting_value"], float)


@pytest.mark.parametrize(
    "fee_rate",
    [
        None,
        "not-a-number",
        float("nan"),
        float("inf"),
        float("-inf"),
        -0.001,
    ],
)
def test_invalid_numeric_fee_rates_are_rejected(
    valuation,
    fee_rate,
):
    route = valid_route()
    route["legs"][0]["fee_rate"] = fee_rate

    with pytest.raises(
        ValueError,
        match="fee_rate must be non-negative",
    ):
        valuation.evaluate(
            route=route,
            starting_value=1000.0,
        )


def test_missing_fee_rate_defaults_to_zero(
    valuation,
):
    route = valid_route()
    del route["legs"][0]["fee_rate"]

    result = valuation.evaluate(
        route=route,
        starting_value=1000.0,
    )

    assert result["legs"][0]["fee_rate"] == 0.0


@pytest.mark.parametrize(
    "market_price",
    [
        None,
        "not-a-number",
        float("nan"),
        float("inf"),
        float("-inf"),
        0.0,
        -1.0,
    ],
)
@pytest.mark.parametrize(
    "side",
    ["buy", "sell"],
)
def test_invalid_numeric_market_prices_are_rejected(
    market_price,
    side,
):
    class InvalidPriceProvider:
        def get_ask(self, symbol):
            return market_price

        def get_bid(self, symbol):
            return market_price

    valuation = FeeAwareLiveRouteValuation(
        InvalidPriceProvider()
    )
    route = {
        "route_id": "ROUTE-INVALID-PRICE",
        "legs": [
            {
                "symbol": "BTC/USDT",
                "side": side,
                "fee_rate": 0.004,
            }
        ],
    }

    with pytest.raises(
        ValueError,
        match="market price unavailable",
    ):
        valuation.evaluate(
            route=route,
            starting_value=1000.0,
        )


def test_numeric_string_fee_rate_is_normalized(
    valuation,
):
    route = valid_route()
    route["legs"][0]["fee_rate"] = "0.004"

    result = valuation.evaluate(
        route=route,
        starting_value=1000.0,
    )

    assert result["legs"][0]["fee_rate"] == 0.004
    assert isinstance(
        result["legs"][0]["fee_rate"],
        float,
    )


def test_fee_rate_of_one_is_allowed_and_produces_zero_net_output(
    valuation,
):
    route = {
        "route_id": "ROUTE-FULL-FEE",
        "legs": [
            {
                "symbol": "BTC/USDT",
                "side": "buy",
                "fee_rate": 1.0,
            }
        ],
    }

    result = valuation.evaluate(
        route=route,
        starting_value=1000.0,
    )

    assert result["legs"][0]["net_output_amount"] == 0.0
    assert result["gross_final_value"] == 0.0
    assert result["total_fee_rate_effect"] == 1.0


def test_fee_rate_above_one_is_rejected(
    valuation,
):
    route = valid_route()
    route["legs"][0]["fee_rate"] = 1.001

    with pytest.raises(
        ValueError,
        match="fee_rate must be between 0 and 1",
    ):
        valuation.evaluate(
            route=route,
            starting_value=1000.0,
        )
