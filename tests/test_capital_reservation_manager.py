import pytest

from exchanges.capital_reservation_manager import (
    CapitalReservationManager,
)


@pytest.fixture
def manager():
    return CapitalReservationManager()


def test_reserves_capital_for_execution(manager):
    result = manager.reserve(
        reservation_id="RES-001",
        amount=200.0,
        available_capital=1000.0,
    )

    assert result["reserved"] is True
    assert result["reservation_id"] == "RES-001"
    assert result["amount"] == 200.0
    assert result["remaining_available_capital"] == 800.0


def test_rejects_reservation_above_available_capital(manager):
    result = manager.reserve(
        reservation_id="RES-002",
        amount=1200.0,
        available_capital=1000.0,
    )

    assert result["reserved"] is False
    assert result["reason"] == "insufficient_available_capital"


def test_releases_reserved_capital(manager):
    manager.reserve(
        reservation_id="RES-003",
        amount=300.0,
        available_capital=1000.0,
    )

    result = manager.release("RES-003")

    assert result["released"] is True
    assert result["reservation_id"] == "RES-003"
    assert result["amount"] == 300.0


def test_rejects_duplicate_reservation_id(manager):
    manager.reserve(
        reservation_id="RES-004",
        amount=100.0,
        available_capital=1000.0,
    )

    with pytest.raises(ValueError, match="reservation_id already exists"):
        manager.reserve(
            reservation_id="RES-004",
            amount=50.0,
            available_capital=1000.0,
        )


def test_gets_reservation(manager):
    manager.reserve(
        reservation_id="RES-005",
        amount=150.0,
        available_capital=1000.0,
    )

    result = manager.get_reservation("RES-005")

    assert result["reservation_id"] == "RES-005"
    assert result["amount"] == 150.0


def test_reports_total_reserved_capital(manager):
    manager.reserve("RES-006", 100.0, 1000.0)
    manager.reserve("RES-007", 250.0, 1000.0)

    assert manager.total_reserved() == 350.0


def test_missing_reservation_id_is_rejected(manager):
    with pytest.raises(ValueError, match="reservation_id is required"):
        manager.reserve("", 100.0, 1000.0)


def test_non_positive_amount_is_rejected(manager):
    with pytest.raises(ValueError, match="amount must be positive"):
        manager.reserve("RES-008", 0.0, 1000.0)
