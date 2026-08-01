import pytest

from exchanges.execution_readiness_validation import ExecutionReadinessValidation


def test_accepts_ready_execution():
    result = ExecutionReadinessValidation.validate(
        exchange_connected=True,
        account_valid=True,
        trading_pair_active=True,
        sufficient_balance=True,
        gas_available=True,
        withdrawal_enabled=True,
    )

    assert result["ready"] is True
    assert result["reason"] is None


def test_rejects_when_exchange_not_connected():
    result = ExecutionReadinessValidation.validate(
        exchange_connected=False,
        account_valid=True,
        trading_pair_active=True,
        sufficient_balance=True,
        gas_available=True,
        withdrawal_enabled=True,
    )

    assert result["ready"] is False
    assert result["reason"] == "exchange_not_connected"


def test_rejects_invalid_account():
    result = ExecutionReadinessValidation.validate(
        exchange_connected=True,
        account_valid=False,
        trading_pair_active=True,
        sufficient_balance=True,
        gas_available=True,
        withdrawal_enabled=True,
    )

    assert result["ready"] is False
    assert result["reason"] == "invalid_account"


def test_rejects_inactive_trading_pair():
    result = ExecutionReadinessValidation.validate(
        exchange_connected=True,
        account_valid=True,
        trading_pair_active=False,
        sufficient_balance=True,
        gas_available=True,
        withdrawal_enabled=True,
    )

    assert result["ready"] is False
    assert result["reason"] == "trading_pair_inactive"


def test_rejects_insufficient_balance():
    result = ExecutionReadinessValidation.validate(
        exchange_connected=True,
        account_valid=True,
        trading_pair_active=True,
        sufficient_balance=False,
        gas_available=True,
        withdrawal_enabled=True,
    )

    assert result["ready"] is False
    assert result["reason"] == "insufficient_balance"


def test_rejects_missing_gas_asset():
    result = ExecutionReadinessValidation.validate(
        exchange_connected=True,
        account_valid=True,
        trading_pair_active=True,
        sufficient_balance=True,
        gas_available=False,
        withdrawal_enabled=True,
    )

    assert result["ready"] is False
    assert result["reason"] == "gas_unavailable"


def test_rejects_disabled_withdrawal():
    result = ExecutionReadinessValidation.validate(
        exchange_connected=True,
        account_valid=True,
        trading_pair_active=True,
        sufficient_balance=True,
        gas_available=True,
        withdrawal_enabled=False,
    )

    assert result["ready"] is False
    assert result["reason"] == "withdrawal_disabled"


def test_rejects_invalid_boolean_inputs():
    with pytest.raises(ValueError):
        ExecutionReadinessValidation.validate(
            exchange_connected="yes",
            account_valid=True,
            trading_pair_active=True,
            sufficient_balance=True,
            gas_available=True,
            withdrawal_enabled=True,
        )
