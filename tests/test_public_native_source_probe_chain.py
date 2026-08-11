from exchanges.public_native_source_probe_chain import (
    PublicNativeSourceProbeChain,
)


class Exchange:
    id = "digifinex"

    def publicSpotGetMarketSymbols(self):
        raise RuntimeError(
            "primary unavailable"
        )

    def publicSpotGetSpotSymbols(self):
        return {
            "data": [
                {
                    "symbol": "BTC_USDT",
                },
            ],
        }


def test_falls_back_to_next_approved_method():
    result = PublicNativeSourceProbeChain().probe(
        exchange=Exchange(),
        method_names=[
            "publicSpotGetMarketSymbols",
            "publicSpotGetSpotSymbols",
        ],
    )

    assert result["probe_success"] is True
    assert result["successful_method"] == (
        "publicSpotGetSpotSymbols"
    )

    assert result["attempt_count"] == 2

    assert result["attempts"][0][
        "probe_success"
    ] is False

    assert result["attempts"][1][
        "probe_success"
    ] is True


def test_stops_after_first_success():
    class SuccessExchange:
        id = "test"

        def publicGetFirst(self):
            return {"data": []}

        def publicGetSecond(self):
            raise AssertionError(
                "second method must not execute"
            )

    result = PublicNativeSourceProbeChain().probe(
        exchange=SuccessExchange(),
        method_names=[
            "publicGetFirst",
            "publicGetSecond",
        ],
    )

    assert result["probe_success"] is True
    assert result["attempt_count"] == 1
    assert result["successful_method"] == (
        "publicGetFirst"
    )


def test_all_failures_are_preserved():
    class FailedExchange:
        id = "test"

        def publicGetFirst(self):
            raise TimeoutError("timeout")

        def publicGetSecond(self):
            raise RuntimeError("failure")

    result = PublicNativeSourceProbeChain().probe(
        exchange=FailedExchange(),
        method_names=[
            "publicGetFirst",
            "publicGetSecond",
        ],
    )

    assert result["probe_success"] is False
    assert result["successful_method"] is None
    assert result["attempt_count"] == 2

    assert [
        item["error_type"]
        for item in result["attempts"]
    ] == [
        "TimeoutError",
        "RuntimeError",
    ]


def test_requires_exchange():
    try:
        PublicNativeSourceProbeChain().probe(
            exchange=None,
            method_names=["publicGetSymbols"],
        )
        assert False
    except ValueError as exc:
        assert str(exc) == "exchange is required"


def test_requires_method_names():
    try:
        PublicNativeSourceProbeChain().probe(
            exchange=Exchange(),
            method_names=None,
        )
        assert False
    except ValueError as exc:
        assert str(exc) == "method_names are required"


def test_chain_is_public_only():
    result = PublicNativeSourceProbeChain().probe(
        exchange=Exchange(),
        method_names=[
            "publicSpotGetMarketSymbols",
            "publicSpotGetSpotSymbols",
        ],
    )

    assert result["public_api_called"] is True
    assert result["live_order_submitted"] is False
