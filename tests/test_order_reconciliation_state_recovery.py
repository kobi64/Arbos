import pytest

from exchanges.order_reconciliation_state_recovery import (
    OrderReconciliationStateRecovery,
)


@pytest.fixture
def engine():
    return OrderReconciliationStateRecovery()


def test_matching_order_is_reconciled(engine):
    local = {
        "order_id": "A1",
        "status": "open",
        "filled": 0.0,
        "amount": 10.0,
    }
    remote = dict(local)

    result = engine.reconcile(local, remote)

    assert result["state"] == "MATCHED"
    assert result["recovery_required"] is False


def test_remote_status_wins_when_exchange_is_newer(engine):
    local = {
        "order_id": "A1",
        "status": "open",
        "filled": 0.0,
        "amount": 10.0,
    }
    remote = {
        "order_id": "A1",
        "status": "closed",
        "filled": 10.0,
        "amount": 10.0,
    }

    result = engine.reconcile(local, remote)

    assert result["state"] == "REMOTE_STATE_CHANGED"
    assert result["resolved_status"] == "closed"
    assert result["resolved_filled"] == 10.0


def test_partial_fill_difference_is_detected(engine):
    local = {
        "order_id": "A1",
        "status": "open",
        "filled": 2.0,
        "amount": 10.0,
    }
    remote = {
        "order_id": "A1",
        "status": "open",
        "filled": 6.0,
        "amount": 10.0,
    }

    result = engine.reconcile(local, remote)

    assert result["state"] == "FILL_MISMATCH"
    assert result["resolved_filled"] == 6.0
    assert result["recovery_required"] is True


def test_missing_remote_order_is_flagged(engine):
    local = {
        "order_id": "A1",
        "status": "open",
        "filled": 0.0,
        "amount": 10.0,
    }

    result = engine.reconcile(local, None)

    assert result["state"] == "REMOTE_MISSING"
    assert result["recovery_required"] is True


def test_unknown_remote_order_is_detected(engine):
    remote = {
        "order_id": "A1",
        "status": "open",
        "filled": 0.0,
        "amount": 10.0,
    }

    result = engine.reconcile(None, remote)

    assert result["state"] == "LOCAL_MISSING"
    assert result["recovery_required"] is True


def test_both_missing_returns_no_order(engine):
    result = engine.reconcile(None, None)

    assert result["state"] == "NO_ORDER"
    assert result["recovery_required"] is False


def test_mismatched_order_ids_are_rejected(engine):
    local = {
        "order_id": "A1",
        "status": "open",
        "filled": 0.0,
        "amount": 10.0,
    }
    remote = {
        "order_id": "B2",
        "status": "open",
        "filled": 0.0,
        "amount": 10.0,
    }

    with pytest.raises(ValueError, match="order IDs do not match"):
        engine.reconcile(local, remote)


def test_recovery_action_is_generated(engine):
    local = {
        "order_id": "A1",
        "status": "open",
        "filled": 1.0,
        "amount": 10.0,
    }
    remote = {
        "order_id": "A1",
        "status": "open",
        "filled": 5.0,
        "amount": 10.0,
    }

    result = engine.reconcile(local, remote)

    assert result["recovery_action"] == "SYNC_FROM_EXCHANGE"
