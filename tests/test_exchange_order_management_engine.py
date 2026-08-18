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


# EX-333 — order lifecycle identity immutability audit


def test_get_order_returns_snapshot_not_internal_record():

    engine = ExchangeOrderManagementEngine()

    created = engine.create_order(
        "HTX",
        "BTC/USDT",
        "BUY",
        100,
    )

    order_id = created["order_id"]

    exposed = engine.get_order(order_id)

    exposed["exchange"] = "KUCOIN"
    exposed["symbol"] = "ETH/USDT"
    exposed["side"] = "SELL"
    exposed["amount"] = 999
    exposed["status"] = "CORRUPTED"

    stored = engine.get_order(order_id)

    assert stored["exchange"] == "HTX"
    assert stored["symbol"] == "BTC/USDT"
    assert stored["side"] == "BUY"
    assert stored["amount"] == 100
    assert stored["status"] == "CREATED"


def test_update_status_preserves_order_identity():

    engine = ExchangeOrderManagementEngine()

    created = engine.create_order(
        "HTX",
        "BTC/USDT",
        "BUY",
        100,
    )

    order_id = created["order_id"]

    before = engine.get_order(order_id)

    result = engine.update_status(
        order_id,
        "FILLED",
    )

    after = engine.get_order(order_id)

    for field in (
        "order_id",
        "exchange",
        "symbol",
        "side",
        "amount",
    ):
        assert result[field] == before[field]
        assert after[field] == before[field]

    assert result["status"] == "FILLED"
    assert after["status"] == "FILLED"


def test_update_status_result_cannot_mutate_internal_record():

    engine = ExchangeOrderManagementEngine()

    created = engine.create_order(
        "HTX",
        "BTC/USDT",
        "BUY",
        100,
    )

    order_id = created["order_id"]

    result = engine.update_status(
        order_id,
        "FILLED",
    )

    result["exchange"] = "KUCOIN"
    result["symbol"] = "ETH/USDT"
    result["side"] = "SELL"
    result["amount"] = 999
    result["status"] = "CORRUPTED"

    stored = engine.get_order(order_id)

    assert stored["exchange"] == "HTX"
    assert stored["symbol"] == "BTC/USDT"
    assert stored["side"] == "BUY"
    assert stored["amount"] == 100
    assert stored["status"] == "FILLED"


def test_cancel_order_preserves_order_identity():

    engine = ExchangeOrderManagementEngine()

    created = engine.create_order(
        "HTX",
        "BTC/USDT",
        "BUY",
        100,
    )

    order_id = created["order_id"]

    before = engine.get_order(order_id)

    result = engine.cancel_order(order_id)

    after = engine.get_order(order_id)

    for field in (
        "order_id",
        "exchange",
        "symbol",
        "side",
        "amount",
    ):
        assert result[field] == before[field]
        assert after[field] == before[field]

    assert result["status"] == "CANCELLED"
    assert after["status"] == "CANCELLED"


def test_cancel_order_result_cannot_mutate_internal_record():

    engine = ExchangeOrderManagementEngine()

    created = engine.create_order(
        "HTX",
        "BTC/USDT",
        "BUY",
        100,
    )

    order_id = created["order_id"]

    result = engine.cancel_order(order_id)

    result["exchange"] = "KUCOIN"
    result["symbol"] = "ETH/USDT"
    result["side"] = "SELL"
    result["amount"] = 999
    result["status"] = "CORRUPTED"

    stored = engine.get_order(order_id)

    assert stored["exchange"] == "HTX"
    assert stored["symbol"] == "BTC/USDT"
    assert stored["side"] == "BUY"
    assert stored["amount"] == 100
    assert stored["status"] == "CANCELLED"


def test_history_returns_snapshots_not_internal_records():

    engine = ExchangeOrderManagementEngine()

    created = engine.create_order(
        "HTX",
        "BTC/USDT",
        "BUY",
        100,
    )

    order_id = created["order_id"]

    history = engine.get_history()

    history[0]["exchange"] = "KUCOIN"
    history[0]["symbol"] = "ETH/USDT"
    history[0]["side"] = "SELL"
    history[0]["amount"] = 999
    history[0]["status"] = "CORRUPTED"

    stored = engine.get_order(order_id)

    assert stored["exchange"] == "HTX"
    assert stored["symbol"] == "BTC/USDT"
    assert stored["side"] == "BUY"
    assert stored["amount"] == 100
    assert stored["status"] == "CREATED"
