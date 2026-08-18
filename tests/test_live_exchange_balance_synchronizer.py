import pytest

from exchanges.exchange_balance_account_state_manager import (
    ExchangeBalanceAccountStateManager,
)
from exchanges.live_exchange_balance_synchronizer import (
    LiveExchangeBalanceSynchronizer,
)


@pytest.fixture
def state_manager():
    return ExchangeBalanceAccountStateManager()


@pytest.fixture
def synchronizer(state_manager):
    return LiveExchangeBalanceSynchronizer(state_manager)


def sample_balance_response():
    return {
        "free": {"USDT": 750.0, "BTC": 0.01},
        "used": {"USDT": 250.0, "BTC": 0.002},
        "total": {"USDT": 1000.0, "BTC": 0.012},
    }


def test_sync_updates_total_balances(synchronizer, state_manager):
    result = synchronizer.sync(
        exchange="kraken",
        balance_response=sample_balance_response(),
    )

    assert result["exchange"] == "kraken"
    assert state_manager.get_balance("kraken", "USDT") == 1000.0
    assert state_manager.get_balance("kraken", "BTC") == 0.012


def test_sync_returns_free_used_and_total_balances(synchronizer):
    result = synchronizer.sync(
        exchange="kraken",
        balance_response=sample_balance_response(),
    )

    assert result["balances"]["USDT"]["free"] == 750.0
    assert result["balances"]["USDT"]["used"] == 250.0
    assert result["balances"]["USDT"]["total"] == 1000.0


def test_missing_free_or_used_values_remain_unknown(synchronizer):
    response = {
        "free": {"USDT": 500.0},
        "used": {},
        "total": {"USDT": 500.0},
    }

    result = synchronizer.sync(
        exchange="kraken",
        balance_response=response,
    )

    assert result["balances"]["USDT"]["free"] == 500.0
    assert result["balances"]["USDT"]["used"] is None
    assert result["balances"]["USDT"]["total"] == 500.0


def test_missing_exchange_is_rejected(synchronizer):
    with pytest.raises(ValueError, match="exchange is required"):
        synchronizer.sync(
            exchange="",
            balance_response=sample_balance_response(),
        )


def test_missing_balance_response_is_rejected(synchronizer):
    with pytest.raises(ValueError, match="balance_response is required"):
        synchronizer.sync(
            exchange="kraken",
            balance_response=None,
        )


def test_missing_used_balance_remains_unknown(synchronizer):
    response = {
        "free": {"USDT": 500.0},
        "used": {},
        "total": {"USDT": 500.0},
    }

    result = synchronizer.sync(
        exchange="kraken",
        balance_response=response,
    )

    assert result["balances"]["USDT"]["free"] == 500.0
    assert result["balances"]["USDT"]["used"] is None
    assert result["balances"]["USDT"]["total"] == 500.0


def test_missing_free_balance_remains_unknown(synchronizer):
    response = {
        "free": {},
        "used": {"USDT": 100.0},
        "total": {"USDT": 500.0},
    }

    result = synchronizer.sync(
        exchange="kraken",
        balance_response=response,
    )

    assert result["balances"]["USDT"]["free"] is None
    assert result["balances"]["USDT"]["used"] == 100.0
    assert result["balances"]["USDT"]["total"] == 500.0


def test_missing_total_balance_remains_unknown(
    synchronizer,
    state_manager,
):
    response = {
        "free": {"USDT": 500.0},
        "used": {"USDT": 100.0},
        "total": {},
    }

    result = synchronizer.sync(
        exchange="kraken",
        balance_response=response,
    )

    assert result["balances"]["USDT"]["free"] == 500.0
    assert result["balances"]["USDT"]["used"] == 100.0
    assert result["balances"]["USDT"]["total"] is None

    # Unknown total must not become a fabricated account balance.
    assert state_manager.get_balance(
        "kraken",
        "USDT",
    ) is None


def test_explicit_none_balance_values_remain_unknown(
    synchronizer,
):
    response = {
        "free": {"USDT": None},
        "used": {"USDT": None},
        "total": {"USDT": None},
    }

    result = synchronizer.sync(
        exchange="kraken",
        balance_response=response,
    )

    assert result["balances"]["USDT"]["free"] is None
    assert result["balances"]["USDT"]["used"] is None
    assert result["balances"]["USDT"]["total"] is None


def test_genuine_zero_balances_remain_numeric_zero(
    synchronizer,
    state_manager,
):
    response = {
        "free": {"USDT": 0.0},
        "used": {"USDT": 0.0},
        "total": {"USDT": 0.0},
    }

    result = synchronizer.sync(
        exchange="kraken",
        balance_response=response,
    )

    assert result["balances"]["USDT"]["free"] == 0.0
    assert result["balances"]["USDT"]["used"] == 0.0
    assert result["balances"]["USDT"]["total"] == 0.0

    assert state_manager.get_balance(
        "kraken",
        "USDT",
    ) == 0.0
