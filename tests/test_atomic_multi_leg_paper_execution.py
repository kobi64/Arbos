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
