import pytest

from exchanges.execution_position_tracker import ExecutionPositionTracker


def test_create_position_tracker():
    tracker = ExecutionPositionTracker(
        execution_id="ARB-001"
    )

    assert tracker is not None


def test_create_initial_position():
    tracker = ExecutionPositionTracker(
        execution_id="ARB-002"
    )

    result = tracker.add_position(
        asset="USDT",
        amount=1000,
        location="exchange_a",
    )

    assert result["asset"] == "USDT"
    assert result["amount"] == 1000


def test_update_position_after_buy():
    tracker = ExecutionPositionTracker(
        execution_id="ARB-003"
    )

    tracker.add_position(
        asset="USDT",
        amount=1000,
        location="exchange_a",
    )

    result = tracker.update_position(
        asset="TOKEN",
        amount=500000,
        location="exchange_a",
    )

    assert result["asset"] == "TOKEN"
    assert result["amount"] == 500000


def test_track_asset_location():
    tracker = ExecutionPositionTracker(
        execution_id="ARB-004"
    )

    tracker.update_position(
        asset="TOKEN",
        amount=500000,
        location="wallet",
    )

    position = tracker.get_position("TOKEN")

    assert position["location"] == "wallet"


def test_compare_expected_position():
    tracker = ExecutionPositionTracker(
        execution_id="ARB-005"
    )

    tracker.update_position(
        asset="TOKEN",
        amount=500000,
        location="exchange_b",
    )

    result = tracker.compare_position(
        asset="TOKEN",
        expected_amount=500000,
    )

    assert result["status"] == "matched"


def test_detect_position_difference():
    tracker = ExecutionPositionTracker(
        execution_id="ARB-006"
    )

    tracker.update_position(
        asset="TOKEN",
        amount=490000,
        location="exchange_b",
    )

    result = tracker.compare_position(
        asset="TOKEN",
        expected_amount=500000,
    )

    assert result["status"] == "mismatch"


def test_position_history_recorded():
    tracker = ExecutionPositionTracker(
        execution_id="ARB-007"
    )

    tracker.update_position(
        asset="USDT",
        amount=1000,
        location="exchange_a",
    )

    history = tracker.get_history()

    assert len(history) == 2


def test_missing_asset_rejected():
    tracker = ExecutionPositionTracker(
        execution_id="ARB-008"
    )

    with pytest.raises(ValueError):
        tracker.update_position(
            asset="",
            amount=100,
            location="exchange_a",
        )
