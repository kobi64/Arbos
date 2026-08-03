import pytest

from exchanges.order_timeout_escalation import (
    OrderTimeoutEscalationEngine,
)


@pytest.fixture
def engine():
    return OrderTimeoutEscalationEngine(
        warning_seconds=30.0,
        timeout_seconds=60.0,
    )


def test_operation_within_limit_is_ok(engine):
    result = engine.evaluate(elapsed_seconds=10.0)

    assert result["state"] == "OK"
    assert result["escalate"] is False


def test_warning_threshold_is_detected(engine):
    result = engine.evaluate(elapsed_seconds=30.0)

    assert result["state"] == "WARNING"
    assert result["escalate"] is False


def test_between_warning_and_timeout_is_warning(engine):
    result = engine.evaluate(elapsed_seconds=45.0)

    assert result["state"] == "WARNING"
    assert result["escalate"] is False


def test_timeout_threshold_escalates(engine):
    result = engine.evaluate(elapsed_seconds=60.0)

    assert result["state"] == "TIMED_OUT"
    assert result["escalate"] is True
    assert result["reason"] == "TIMEOUT_EXCEEDED"


def test_elapsed_beyond_timeout_escalates(engine):
    result = engine.evaluate(elapsed_seconds=90.0)

    assert result["state"] == "TIMED_OUT"
    assert result["escalate"] is True


def test_negative_elapsed_time_is_rejected(engine):
    with pytest.raises(ValueError, match="elapsed_seconds cannot be negative"):
        engine.evaluate(elapsed_seconds=-1.0)


def test_timeout_must_exceed_warning():
    with pytest.raises(
        ValueError,
        match="timeout_seconds must exceed warning_seconds",
    ):
        OrderTimeoutEscalationEngine(
            warning_seconds=60.0,
            timeout_seconds=30.0,
        )


def test_timeout_and_warning_cannot_be_equal():
    with pytest.raises(
        ValueError,
        match="timeout_seconds must exceed warning_seconds",
    ):
        OrderTimeoutEscalationEngine(
            warning_seconds=60.0,
            timeout_seconds=60.0,
        )


def test_remaining_time_is_reported(engine):
    result = engine.evaluate(elapsed_seconds=20.0)

    assert result["remaining_seconds"] == 40.0


def test_timed_out_remaining_time_is_zero(engine):
    result = engine.evaluate(elapsed_seconds=75.0)

    assert result["remaining_seconds"] == 0.0
