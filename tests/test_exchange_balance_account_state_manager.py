from exchanges.exchange_balance_account_state_manager import ExchangeBalanceAccountStateManager


def test_create_manager():

    manager = ExchangeBalanceAccountStateManager()

    assert manager is not None


def test_add_account_balance():

    manager = ExchangeBalanceAccountStateManager()

    result = manager.update_balance(
        "HTX",
        "USDT",
        1000
    )

    assert result["success"] is True


def test_get_balance():

    manager = ExchangeBalanceAccountStateManager()

    manager.update_balance(
        "HTX",
        "USDT",
        1000
    )

    result = manager.get_balance(
        "HTX",
        "USDT"
    )

    assert result == 1000


def test_validate_funds():

    manager = ExchangeBalanceAccountStateManager()

    manager.update_balance(
        "HTX",
        "USDT",
        1000
    )

    result = manager.validate_funds(
        "HTX",
        "USDT",
        500
    )

    assert result is True


def test_insufficient_funds():

    manager = ExchangeBalanceAccountStateManager()

    manager.update_balance(
        "HTX",
        "USDT",
        100
    )

    result = manager.validate_funds(
        "HTX",
        "USDT",
        500
    )

    assert result is False


def test_account_status():

    manager = ExchangeBalanceAccountStateManager()

    result = manager.set_account_status(
        "HTX",
        "ACTIVE"
    )

    assert result["status"] == "ACTIVE"


def test_account_snapshot():

    manager = ExchangeBalanceAccountStateManager()

    manager.update_balance(
        "HTX",
        "USDT",
        1000
    )

    snapshot = manager.get_snapshot(
        "HTX"
    )

    assert snapshot["exchange"] == "HTX"


def test_missing_balance():

    manager = ExchangeBalanceAccountStateManager()

    result = manager.get_balance(
        "UNKNOWN",
        "USDT"
    )

    assert result is None



def test_missing_asset_balance_remains_unknown():

    manager = ExchangeBalanceAccountStateManager()

    manager.update_balance(
        "HTX",
        "BTC",
        1.0
    )

    result = manager.get_balance(
        "HTX",
        "USDT"
    )

    assert result is None


def test_unknown_balance_fails_funds_validation_closed():

    manager = ExchangeBalanceAccountStateManager()

    result = manager.validate_funds(
        "HTX",
        "USDT",
        100
    )

    assert result is False


def test_genuine_zero_balance_remains_numeric_zero():

    manager = ExchangeBalanceAccountStateManager()

    manager.update_balance(
        "HTX",
        "USDT",
        0
    )

    result = manager.get_balance(
        "HTX",
        "USDT"
    )

    assert result == 0
    assert result is not None


def test_genuine_zero_balance_fails_positive_funds_requirement():

    manager = ExchangeBalanceAccountStateManager()

    manager.update_balance(
        "HTX",
        "USDT",
        0
    )

    result = manager.validate_funds(
        "HTX",
        "USDT",
        1
    )

    assert result is False
