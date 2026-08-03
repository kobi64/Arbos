import pytest

from exchanges.order_cancellation_abort_coordination import (
    OrderCancellationAbortCoordinator,
)


@pytest.fixture
def coordinator():
    return OrderCancellationAbortCoordinator()


def test_pending_order_can_be_aborted(coordinator):
    result = coordinator.evaluate(
        order_state="PENDING",
        abort_requested=True,
    )

    assert result["action"] == "ABORT_WORKFLOW"
    assert result["abort_allowed"] is True
    assert result["escalate"] is False


def test_open_order_should_be_cancelled(coordinator):
    result = coordinator.evaluate(
        order_state="OPEN",
        abort_requested=True,
    )

    assert result["action"] == "CANCEL_ORDER"
    assert result["abort_allowed"] is True


def test_partially_filled_order_requires_cancel_and_reconcile(coordinator):
    result = coordinator.evaluate(
        order_state="PARTIALLY_FILLED",
        abort_requested=True,
    )

    assert result["action"] == "CANCEL_AND_RECONCILE"
    assert result["abort_allowed"] is True
    assert result["reconcile_required"] is True


def test_filled_order_cannot_be_cancelled(coordinator):
    result = coordinator.evaluate(
        order_state="FILLED",
        abort_requested=True,
    )

    assert result["action"] == "NO_CANCEL_POSSIBLE"
    assert result["abort_allowed"] is False
    assert result["escalate"] is True


def test_cancelled_order_needs_no_action(coordinator):
    result = coordinator.evaluate(
        order_state="CANCELLED",
        abort_requested=True,
    )

    assert result["action"] == "ALREADY_CANCELLED"
    assert result["abort_allowed"] is False
    assert result["escalate"] is False


def test_uncertain_state_requires_escalation(coordinator):
    result = coordinator.evaluate(
        order_state="UNKNOWN",
        abort_requested=True,
    )

    assert result["action"] == "RECONCILE_BEFORE_ABORT"
    assert result["abort_allowed"] is False
    assert result["escalate"] is True
    assert result["reconcile_required"] is True


def test_no_abort_request_results_in_no_action(coordinator):
    result = coordinator.evaluate(
        order_state="OPEN",
        abort_requested=False,
    )

    assert result["action"] == "NO_ACTION"
    assert result["abort_allowed"] is False


def test_invalid_order_state_is_rejected(coordinator):
    with pytest.raises(ValueError, match="unsupported order_state"):
        coordinator.evaluate(
            order_state="BANANA",
            abort_requested=True,
        )


def test_none_order_state_is_rejected(coordinator):
    with pytest.raises(ValueError, match="order_state is required"):
        coordinator.evaluate(
            order_state=None,
            abort_requested=True,
        )


def test_state_is_case_insensitive(coordinator):
    result = coordinator.evaluate(
        order_state="open",
        abort_requested=True,
    )

    assert result["action"] == "CANCEL_ORDER"
