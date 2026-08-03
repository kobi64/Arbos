import pytest

from exchanges.order_retry_backoff_policy import (
    OrderRetryBackoffPolicy,
)


@pytest.fixture
def policy():
    return OrderRetryBackoffPolicy(
        max_attempts=3,
        base_delay_seconds=1.0,
        max_delay_seconds=8.0,
    )


def test_retryable_error_allows_retry(policy):
    result = policy.evaluate(
        attempt=1,
        error_type="TIMEOUT",
        execution_uncertain=False,
    )

    assert result["retry"] is True
    assert result["escalate"] is False


def test_non_retryable_error_escalates(policy):
    result = policy.evaluate(
        attempt=1,
        error_type="INVALID_ORDER",
        execution_uncertain=False,
    )

    assert result["retry"] is False
    assert result["escalate"] is True
    assert result["reason"] == "NON_RETRYABLE_ERROR"


def test_uncertain_execution_blocks_retry(policy):
    result = policy.evaluate(
        attempt=1,
        error_type="TIMEOUT",
        execution_uncertain=True,
    )

    assert result["retry"] is False
    assert result["escalate"] is True
    assert result["reason"] == "EXECUTION_STATE_UNCERTAIN"


def test_max_attempts_blocks_retry(policy):
    result = policy.evaluate(
        attempt=3,
        error_type="TIMEOUT",
        execution_uncertain=False,
    )

    assert result["retry"] is False
    assert result["escalate"] is True
    assert result["reason"] == "MAX_ATTEMPTS_REACHED"


def test_exponential_backoff(policy):
    first = policy.evaluate(1, "TIMEOUT", False)
    second = policy.evaluate(2, "TIMEOUT", False)

    assert first["delay_seconds"] == 1.0
    assert second["delay_seconds"] == 2.0


def test_backoff_is_capped():
    policy = OrderRetryBackoffPolicy(
        max_attempts=10,
        base_delay_seconds=2.0,
        max_delay_seconds=5.0,
    )

    result = policy.evaluate(4, "TIMEOUT", False)

    assert result["delay_seconds"] == 5.0


@pytest.mark.parametrize(
    "error_type",
    [
        "TIMEOUT",
        "RATE_LIMIT",
        "TEMPORARY_UNAVAILABLE",
        "NETWORK_ERROR",
    ],
)
def test_known_transient_errors_are_retryable(policy, error_type):
    result = policy.evaluate(
        attempt=1,
        error_type=error_type,
        execution_uncertain=False,
    )

    assert result["retry"] is True


def test_attempt_must_be_positive(policy):
    with pytest.raises(ValueError, match="attempt must be positive"):
        policy.evaluate(
            attempt=0,
            error_type="TIMEOUT",
            execution_uncertain=False,
        )
