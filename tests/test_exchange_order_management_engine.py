from exchanges.exchange_order_management_engine import ExchangeOrderManagementEngine


def test_create_engine():

    engine = ExchangeOrderManagementEngine()

    assert engine is not None


def test_create_order():

    engine = ExchangeOrderManagementEngine()

    result = engine.create_order(
        "HTX",
        "BTC/USDT",
        "BUY",
        100
    )

    assert result["success"] is True


def test_order_id_created():

    engine = ExchangeOrderManagementEngine()

    result = engine.create_order(
        "HTX",
        "BTC/USDT",
        "BUY",
        100
    )

    assert result["order_id"] is not None


def test_get_order():

    engine = ExchangeOrderManagementEngine()

    order = engine.create_order(
        "HTX",
        "BTC/USDT",
        "BUY",
        100
    )

    result = engine.get_order(
        order["order_id"]
    )

    assert result["symbol"] == "BTC/USDT"


def test_update_status():

    engine = ExchangeOrderManagementEngine()

    order = engine.create_order(
        "HTX",
        "BTC/USDT",
        "BUY",
        100
    )

    result = engine.update_status(
        order["order_id"],
        "FILLED"
    )

    assert result["status"] == "FILLED"


def test_cancel_order():

    engine = ExchangeOrderManagementEngine()

    order = engine.create_order(
        "HTX",
        "BTC/USDT",
        "BUY",
        100
    )

    result = engine.cancel_order(
        order["order_id"]
    )

    assert result["status"] == "CANCELLED"


def test_order_history():

    engine = ExchangeOrderManagementEngine()

    engine.create_order(
        "HTX",
        "BTC/USDT",
        "BUY",
        100
    )

    history = engine.get_history()

    assert len(history) == 1


def test_missing_order():

    engine = ExchangeOrderManagementEngine()

    result = engine.get_order(
        "unknown"
    )

    assert result is None
