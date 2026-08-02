from exchanges.exchange_response_parser import ExchangeResponseParser


def test_create_parser():

    parser = ExchangeResponseParser()

    assert parser is not None


def test_parse_success_response():

    parser = ExchangeResponseParser()

    result = parser.parse(
        "HTX",
        {
            "status": "ok",
            "data": {
                "id": "123"
            }
        }
    )

    assert result["success"] is True


def test_extract_order_id():

    parser = ExchangeResponseParser()

    result = parser.extract_order_id(
        {
            "id": "order-001"
        }
    )

    assert result == "order-001"


def test_parse_failure_response():

    parser = ExchangeResponseParser()

    result = parser.parse(
        "HTX",
        {
            "status": "error"
        }
    )

    assert result["success"] is False


def test_normalise_error():

    parser = ExchangeResponseParser()

    result = parser.normalise_error(
        "INVALID_KEY"
    )

    assert result["error"] == "AUTH_ERROR"


def test_extract_balance():

    parser = ExchangeResponseParser()

    result = parser.extract_balance(
        {
            "balance": 100
        }
    )

    assert result == 100


def test_exchange_metadata():

    parser = ExchangeResponseParser()

    result = parser.parse(
        "HTX",
        {
            "status": "ok"
        }
    )

    assert result["exchange"] == "HTX"


def test_invalid_response():

    parser = ExchangeResponseParser()

    result = parser.parse(
        "HTX",
        None
    )

    assert result["success"] is False
