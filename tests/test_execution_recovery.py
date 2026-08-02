import pytest

from exchanges.execution_recovery import ExecutionRecovery


def test_create_recovery_record():
    result = ExecutionRecovery.create_record(
        execution_id="EXEC-100",
        reason="exchange_timeout",
    )

    assert result["status"] == "recovery_created"
    assert result["execution_id"] == "EXEC-100"


def test_failure_moves_to_recovery_pending():
    result = ExecutionRecovery.set_recovery_state(
        execution_id="EXEC-101",
        state="RECOVERY_PENDING",
    )

    assert result["state"] == "RECOVERY_PENDING"


def test_retry_attempt_recorded():
    result = ExecutionRecovery.record_retry(
        execution_id="EXEC-102",
    )

    assert result["status"] == "retry_recorded"
    assert result["attempt"] == 1


def test_multiple_retry_attempts_increment():
    ExecutionRecovery.record_retry(
        execution_id="EXEC-103",
    )

    result = ExecutionRecovery.record_retry(
        execution_id="EXEC-103",
    )

    assert result["attempt"] == 2


def test_recovery_success():
    result = ExecutionRecovery.complete_recovery(
        execution_id="EXEC-104",
        outcome="COMPLETED",
    )

    assert result["status"] == "recovered"
    assert result["outcome"] == "COMPLETED"


def test_recovery_failure():
    result = ExecutionRecovery.fail_recovery(
        execution_id="EXEC-105",
        reason="max_retries_exceeded",
    )

    assert result["status"] == "failed"
    assert result["reason"] == "max_retries_exceeded"


def test_invalid_recovery_state():
    with pytest.raises(ValueError):
        ExecutionRecovery.set_recovery_state(
            execution_id="EXEC-106",
            state="UNKNOWN",
        )


def test_get_recovery_history():
    ExecutionRecovery.record_retry(
        execution_id="EXEC-107",
    )

    result = ExecutionRecovery.get_history(
        execution_id="EXEC-107",
    )

    assert isinstance(result, list)
    assert len(result) >= 1
