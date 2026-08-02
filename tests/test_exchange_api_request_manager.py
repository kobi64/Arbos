from exchanges.exchange_api_request_manager import ExchangeAPIRequestManager


def test_create_request_manager():

    manager = ExchangeAPIRequestManager()

    assert manager is not None


def test_create_request():

    manager = ExchangeAPIRequestManager()

    result = manager.create_request(
        "HTX",
        "/balance",
        "GET"
    )

    assert result["exchange"] == "HTX"


def test_request_method():

    manager = ExchangeAPIRequestManager()

    result = manager.create_request(
        "HTX",
        "/orders",
        "POST"
    )

    assert result["method"] == "POST"


def test_missing_exchange():

    manager = ExchangeAPIRequestManager()

    result = manager.create_request(
        None,
        "/balance",
        "GET"
    )

    assert result["success"] is False


def test_timeout_handling():

    manager = ExchangeAPIRequestManager()

    result = manager.handle_timeout(
        "HTX"
    )

    assert result["status"] == "TIMEOUT"


def test_retry_logic():

    manager = ExchangeAPIRequestManager()

    result = manager.retry_request(
        "request-001"
    )

    assert result["retry"] is True


def test_error_normalisation():

    manager = ExchangeAPIRequestManager()

    result = manager.normalise_error(
        "API_LIMIT"
    )

    assert result["error"] == "RATE_LIMIT"


def test_request_history():

    manager = ExchangeAPIRequestManager()

    manager.create_request(
        "HTX",
        "/balance",
        "GET"
    )

    history = manager.get_history()

    assert len(history) == 1
