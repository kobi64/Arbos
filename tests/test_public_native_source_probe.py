from exchanges.public_native_source_probe import (
    PublicNativeSourceProbe,
)


class SuccessExchange:
    id = "gate"

    def publicSpotGetCurrencyPairs(self):
        return {
            "data": [
                {"id": "BTC_USDT"},
                {"id": "ETH_USDT"},
            ]
        }


class FailureExchange:
    id = "gate"

    def publicSpotGetCurrencyPairs(self):
        raise TimeoutError(
            "public API timeout"
        )


def test_executes_selected_public_method():
    result = PublicNativeSourceProbe().probe(
        exchange=SuccessExchange(),
        method_name="publicSpotGetCurrencyPairs",
    )

    assert result["exchange_id"] == "gate"
    assert result["method"] == (
        "publicSpotGetCurrencyPairs"
    )
    assert result["probe_success"] is True
    assert result["response_type"] == "dict"
    assert result["response"] == {
        "data": [
            {"id": "BTC_USDT"},
            {"id": "ETH_USDT"},
        ]
    }


def test_records_public_method_failure():
    result = PublicNativeSourceProbe().probe(
        exchange=FailureExchange(),
        method_name="publicSpotGetCurrencyPairs",
    )

    assert result["probe_success"] is False
    assert result["error_type"] == "TimeoutError"
    assert result["error"] == "public API timeout"


def test_missing_method_is_reported():
    result = PublicNativeSourceProbe().probe(
        exchange=SuccessExchange(),
        method_name="publicSpotGetMissing",
    )

    assert result["probe_success"] is False
    assert result["error_type"] == "MethodUnavailable"


def test_requires_exchange():
    try:
        PublicNativeSourceProbe().probe(
            exchange=None,
            method_name="publicGetSymbols",
        )
        assert False
    except ValueError as exc:
        assert str(exc) == "exchange is required"


def test_requires_method_name():
    try:
        PublicNativeSourceProbe().probe(
            exchange=SuccessExchange(),
            method_name="",
        )
        assert False
    except ValueError as exc:
        assert str(exc) == "method_name is required"


def test_probe_is_public_only():
    result = PublicNativeSourceProbe().probe(
        exchange=SuccessExchange(),
        method_name="publicSpotGetCurrencyPairs",
    )

    assert result["public_api_called"] is True
    assert result["live_order_submitted"] is False
