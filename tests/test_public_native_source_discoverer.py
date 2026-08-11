from exchanges.public_native_source_discoverer import (
    PublicNativeSourceDiscoverer,
)


class FakeExchange:
    id = "gateio"

    def publicSpotGetCurrencyPairs(self):
        return {}

    def publicSpotGetOrderBook(self):
        return {}

    def privatePostOrders(self):
        return {}


class EmptyExchange:
    id = "empty"


def test_discovers_public_market_catalogue_candidate():
    result = PublicNativeSourceDiscoverer().discover(
        FakeExchange()
    )

    assert result["exchange_id"] == "gateio"

    assert (
        "publicSpotGetCurrencyPairs"
        in result["candidate_methods"]
    )

    assert result["candidate_count"] == 1
    assert result["discovery_complete"] is True
    assert result["live_order_submitted"] is False


def test_excludes_order_book_methods():
    result = PublicNativeSourceDiscoverer().discover(
        FakeExchange()
    )

    assert (
        "publicSpotGetOrderBook"
        not in result["candidate_methods"]
    )


def test_excludes_private_methods():
    result = PublicNativeSourceDiscoverer().discover(
        FakeExchange()
    )

    assert (
        "privatePostOrders"
        not in result["candidate_methods"]
    )


def test_empty_exchange_is_supported():
    result = PublicNativeSourceDiscoverer().discover(
        EmptyExchange()
    )

    assert result["exchange_id"] == "empty"
    assert result["candidate_methods"] == []
    assert result["candidate_count"] == 0
    assert result["discovery_complete"] is True


def test_none_exchange_rejected():
    try:
        PublicNativeSourceDiscoverer().discover(
            None
        )
    except ValueError as exc:
        assert str(exc) == "exchange is required"
    else:
        raise AssertionError(
            "ValueError was not raised"
        )


def test_discovery_does_not_call_candidate_method():
    class Exchange:
        id = "safe"

        def publicGetSymbols(self):
            raise AssertionError(
                "discovery must not execute API method"
            )

    result = PublicNativeSourceDiscoverer().discover(
        Exchange()
    )

    assert result["candidate_methods"] == [
        "publicGetSymbols"
    ]
    assert result["live_order_submitted"] is False
