from exchanges.exchange_adapter_layer import ExchangeAdapterLayer


def test_create_adapter():

    adapter = ExchangeAdapterLayer("HTX")

    assert adapter.exchange_name == "HTX"


def test_supported_exchange():

    adapter = ExchangeAdapterLayer("Gate")

    assert adapter.is_supported() is True


def test_unsupported_exchange():

    adapter = ExchangeAdapterLayer("UNKNOWN")

    assert adapter.is_supported() is False


def test_get_balance():

    adapter = ExchangeAdapterLayer("HTX")

    result = adapter.get_balance("USDT")

    assert result["asset"] == "USDT"


def test_create_order():

    adapter = ExchangeAdapterLayer("HTX")

    result = adapter.create_order(
        "BTC/USDT",
        "BUY",
        100
    )

    assert result["symbol"] == "BTC/USDT"


def test_order_status():

    adapter = ExchangeAdapterLayer("HTX")

    result = adapter.get_order_status("order-001")

    assert result["order_id"] == "order-001"


def test_exchange_error():

    adapter = ExchangeAdapterLayer("UNKNOWN")

    result = adapter.create_order(
        "BTC/USDT",
        "BUY",
        100
    )

    assert result["success"] is False


def test_adapter_information():

    adapter = ExchangeAdapterLayer("HTX")

    info = adapter.info()

    assert info["exchange"] == "HTX"


def test_supported_exchange_unknown_balance_is_not_zero():
    adapter = ExchangeAdapterLayer("HTX")

    result = adapter.get_balance("USDT")

    assert result["success"] is True
    assert result["asset"] == "USDT"
    assert result["balance"] is None


def test_unknown_balance_is_distinct_from_real_zero_balance():
    adapter = ExchangeAdapterLayer("Gate")

    result = adapter.get_balance("BTC")

    # The adapter has not actually queried a live account.
    # Therefore zero must not be fabricated.
    assert result["balance"] is None


def test_unsupported_exchange_does_not_report_balance():
    adapter = ExchangeAdapterLayer("UNKNOWN")

    result = adapter.get_balance("USDT")

    assert result["success"] is False
    assert result["reason"] == "unsupported_exchange"
    assert "balance" not in result
