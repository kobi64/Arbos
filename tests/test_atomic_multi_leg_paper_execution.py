import pytest

from exchanges.atomic_multi_leg_paper_execution import (
    AtomicMultiLegPaperExecution,
)


@pytest.fixture
def simulator():
    return AtomicMultiLegPaperExecution()


def frozen_snapshot():
    return {
        "route_id": "ROUTE-001",
        "snapshots": [
            {
                "symbol": "BTC/USDT",
                "bids": [[61900.0, 1.0]],
                "asks": [[62000.0, 1.0]],
            },
            {
                "symbol": "ETH/BTC",
                "bids": [[0.049, 10.0]],
                "asks": [[0.05, 10.0]],
            },
            {
                "symbol": "ETH/USDT",
                "bids": [[3200.0, 10.0]],
                "asks": [[3210.0, 10.0]],
            },
        ],
    }


def valid_route():
    return {
        "route_id": "ROUTE-001",
        "legs": [
            {"symbol": "BTC/USDT", "side": "buy"},
            {"symbol": "ETH/BTC", "side": "buy"},
            {"symbol": "ETH/USDT", "side": "sell"},
        ],
    }


def test_executes_all_legs_from_frozen_snapshots(simulator):
    result = simulator.execute(
        route=valid_route(),
        atomic_snapshot=frozen_snapshot(),
        starting_value=1000.0,
    )

    assert result["route_id"] == "ROUTE-001"
    assert result["status"] == "COMPLETED"
    assert len(result["legs"]) == 3


def test_executes_all_legs_from_frozen_snapshots(simulator):
    result = simulator.execute(
        route=valid_route(),
        atomic_snapshot=frozen_snapshot(),
        starting_value=1000.0,
    )

    assert result["route_id"] == "ROUTE-001"
    assert result["status"] == "COMPLETED"
    assert len(result["legs"]) == 3


def test_each_leg_uses_matching_snapshot(simulator):
    result = simulator.execute(
        route=valid_route(),
        atomic_snapshot=frozen_snapshot(),
        starting_value=1000.0,
    )

    assert result["legs"][0]["symbol"] == "BTC/USDT"
    assert result["legs"][1]["symbol"] == "ETH/BTC"
    assert result["legs"][2]["symbol"] == "ETH/USDT"


def test_missing_route_is_rejected(simulator):
    with pytest.raises(ValueError, match="route is required"):
        simulator.execute(
            route=None,
            atomic_snapshot=frozen_snapshot(),
            starting_value=1000.0,
        )


def test_missing_atomic_snapshot_is_rejected(simulator):
    with pytest.raises(ValueError, match="atomic_snapshot is required"):
        simulator.execute(
            route=valid_route(),
            atomic_snapshot=None,
            starting_value=1000.0,
        )


def test_mismatched_snapshot_symbol_is_rejected(simulator):
    snapshot = frozen_snapshot()
    snapshot["snapshots"][1]["symbol"] = "SOL/BTC"

    with pytest.raises(ValueError, match="snapshot symbol mismatch"):
        simulator.execute(
            route=valid_route(),
            atomic_snapshot=snapshot,
            starting_value=1000.0,
        )


def test_invalid_starting_value_is_rejected(simulator):
    with pytest.raises(ValueError, match="starting_value must be positive"):
        simulator.execute(
            route=valid_route(),
            atomic_snapshot=frozen_snapshot(),
            starting_value=0.0,
        )


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
    simulator,
    starting_value,
):
    with pytest.raises(
        ValueError,
        match="starting_value must be positive",
    ):
        simulator.execute(
            route=valid_route(),
            atomic_snapshot=frozen_snapshot(),
            starting_value=starting_value,
        )


@pytest.mark.parametrize(
    "side,book_name,price",
    [
        ("buy", "asks", None),
        ("buy", "asks", "not-a-number"),
        ("buy", "asks", float("nan")),
        ("buy", "asks", float("inf")),
        ("buy", "asks", float("-inf")),
        ("buy", "asks", 0.0),
        ("buy", "asks", -1.0),
        ("sell", "bids", None),
        ("sell", "bids", "not-a-number"),
        ("sell", "bids", float("nan")),
        ("sell", "bids", float("inf")),
        ("sell", "bids", float("-inf")),
        ("sell", "bids", 0.0),
        ("sell", "bids", -1.0),
    ],
)
def test_invalid_numeric_top_of_book_prices_are_rejected(
    simulator,
    side,
    book_name,
    price,
):
    route = {
        "route_id": "ROUTE-PRICE",
        "legs": [
            {
                "symbol": "BTC/USDT",
                "side": side,
            },
        ],
    }

    snapshot = {
        "route_id": "ROUTE-PRICE",
        "snapshots": [
            {
                "symbol": "BTC/USDT",
                "bids": [[62000.0, 1.0]],
                "asks": [[62000.0, 1.0]],
            },
        ],
    }

    snapshot["snapshots"][0][book_name][0][0] = price

    with pytest.raises(
        ValueError,
        match="order book price unavailable",
    ):
        simulator.execute(
            route=route,
            atomic_snapshot=snapshot,
            starting_value=1000.0,
        )


@pytest.mark.parametrize(
    "side,book_name",
    [
        ("buy", "asks"),
        ("sell", "bids"),
    ],
)
def test_malformed_top_of_book_level_is_rejected(
    simulator,
    side,
    book_name,
):
    route = {
        "route_id": "ROUTE-LEVEL",
        "legs": [
            {
                "symbol": "BTC/USDT",
                "side": side,
            },
        ],
    }

    snapshot = {
        "route_id": "ROUTE-LEVEL",
        "snapshots": [
            {
                "symbol": "BTC/USDT",
                "bids": [[62000.0, 1.0]],
                "asks": [[62000.0, 1.0]],
            },
        ],
    }

    snapshot["snapshots"][0][book_name] = [[]]

    with pytest.raises(
        ValueError,
        match="order book price unavailable",
    ):
        simulator.execute(
            route=route,
            atomic_snapshot=snapshot,
            starting_value=1000.0,
        )


def test_numeric_strings_are_normalized_to_floats(simulator):
    snapshot = frozen_snapshot()

    snapshot["snapshots"][0]["asks"][0][0] = "62000"
    snapshot["snapshots"][1]["asks"][0][0] = "0.05"
    snapshot["snapshots"][2]["bids"][0][0] = "3200"

    result = simulator.execute(
        route=valid_route(),
        atomic_snapshot=snapshot,
        starting_value="1000",
    )

    assert result["starting_value"] == 1000.0
    assert isinstance(result["starting_value"], float)

    for leg in result["legs"]:
        assert isinstance(leg["input_amount"], float)
        assert isinstance(leg["average_price"], float)
        assert isinstance(leg["output_amount"], float)

    assert isinstance(result["final_value"], float)


def test_successful_outputs_are_finite_and_positive(simulator):
    result = simulator.execute(
        route=valid_route(),
        atomic_snapshot=frozen_snapshot(),
        starting_value=1000.0,
    )

    import math

    assert math.isfinite(result["starting_value"])
    assert result["starting_value"] > 0

    assert math.isfinite(result["final_value"])
    assert result["final_value"] > 0

    for leg in result["legs"]:
        assert math.isfinite(leg["input_amount"])
        assert leg["input_amount"] > 0

        assert math.isfinite(leg["average_price"])
        assert leg["average_price"] > 0

        assert math.isfinite(leg["output_amount"])
        assert leg["output_amount"] > 0
