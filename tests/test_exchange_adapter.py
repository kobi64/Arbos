import pytest

from exchanges.exchange_adapter import ExchangeAdapter


def test_create_adapter():
    adapter = ExchangeAdapter(
        exchange_name="HTX"
    )

    assert adapter.exchange_name == "HTX"


def test_validate_connection():
    adapter = ExchangeAdapter(
        exchange_name="GateIO"
    )

    result = adapter.validate_connection()

    assert result["status"] == "ready"


def test_prepare_order():
    adapter = ExchangeAdapter(
        exchange_name="Bitget"
    )

    result = adapter.prepare_order(
        symbol="BTC/USDT",
        side="BUY",
        amount=100,
    )

    assert result["status"] == "prepared"
    assert result["symbol"] == "BTC/USDT"


def test_reject_invalid_side():
    adapter = ExchangeAdapter(
        exchange_name="HTX"
    )

    with pytest.raises(ValueError):
        adapter.prepare_order(
            symbol="BTC/USDT",
            side="INVALID",
            amount=100,
        )


def test_execute_simulated_order():
    adapter = ExchangeAdapter(
        exchange_name="HTX"
    )

    result = adapter.execute_order(
        order_id="ORDER-001",
        simulation=True,
    )

    assert result["status"] == "simulated"
    assert result["order_id"] == "ORDER-001"


def test_execute_live_order_requires_permission():
    adapter = ExchangeAdapter(
        exchange_name="HTX"
    )

    result = adapter.execute_order(
        order_id="ORDER-002",
        simulation=False,
    )

    assert result["status"] == "blocked"


def test_get_exchange_status():
    adapter = ExchangeAdapter(
        exchange_name="GateIO"
    )

    result = adapter.get_status()

    assert result["exchange"] == "GateIO"
    assert result["status"] == "available"


def test_missing_exchange_name_rejected():
    with pytest.raises(ValueError):
        ExchangeAdapter(
            exchange_name=""
        )
