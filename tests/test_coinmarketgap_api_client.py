import pytest

from core.coinmarketgap_api_client import (
    CoinMarketGapAPIClient,
)


class FakeResponse:
    def __init__(
        self,
        payload,
        status_code=200,
    ):
        self._payload = payload
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(
                f"HTTP {self.status_code}"
            )

    def json(self):
        return self._payload


class FakeSession:
    def __init__(
        self,
        response,
    ):
        self._response = response
        self.calls = []

    def get(
        self,
        url,
        timeout,
    ):
        self.calls.append({
            "url": url,
            "timeout": timeout,
        })

        return self._response


def rows():
    return [
        {
            "internal_ticker": "COTI",
            "buy_exchange": "kucoin",
            "sell_exchange": "digifinex",
            "exploitable": True,
        },
        {
            "internal_ticker": "IOTX",
            "buy_exchange": "hashkey_exchange",
            "sell_exchange": "gdax",
            "exploitable": False,
        },
    ]


def test_fetches_coinmarketgap_results():
    session = FakeSession(
        FakeResponse({
            "results": rows(),
        })
    )

    client = CoinMarketGapAPIClient(
        session=session,
        timeout_seconds=15,
    )

    result = client.fetch()

    assert result[
        "fetch_complete"
    ] is True

    assert result[
        "result_count"
    ] == 2

    assert result[
        "results"
    ] == rows()

    assert session.calls[0][
        "url"
    ] == (
        "https://www.coinmarket-gap.com/api/arb/"
    )

    assert session.calls[0][
        "timeout"
    ] == 15.0


def test_can_filter_to_exploitable_results():
    session = FakeSession(
        FakeResponse({
            "results": rows(),
        })
    )

    client = CoinMarketGapAPIClient(
        session=session,
    )

    result = client.fetch(
        exploitable_only=True
    )

    assert result[
        "result_count"
    ] == 1

    assert result[
        "results"
    ][0][
        "internal_ticker"
    ] == "COTI"

    assert result[
        "results"
    ][0][
        "exploitable"
    ] is True


def test_default_fetch_keeps_all_results():
    session = FakeSession(
        FakeResponse({
            "results": rows(),
        })
    )

    client = CoinMarketGapAPIClient(
        session=session,
    )

    result = client.fetch()

    assert result[
        "result_count"
    ] == 2


def test_invalid_payload_returns_failed_result():
    session = FakeSession(
        FakeResponse({
            "unexpected": [],
        })
    )

    client = CoinMarketGapAPIClient(
        session=session,
    )

    result = client.fetch()

    assert result[
        "fetch_complete"
    ] is False

    assert result[
        "results"
    ] == []

    assert result[
        "result_count"
    ] == 0


def test_http_failure_returns_failed_result():
    session = FakeSession(
        FakeResponse(
            {},
            status_code=500,
        )
    )

    client = CoinMarketGapAPIClient(
        session=session,
    )

    result = client.fetch()

    assert result[
        "fetch_complete"
    ] is False

    assert result[
        "results"
    ] == []


def test_timeout_must_be_positive():
    with pytest.raises(
        ValueError,
        match="timeout_seconds must be positive",
    ):
        CoinMarketGapAPIClient(
            session=FakeSession(
                FakeResponse({})
            ),
            timeout_seconds=0,
        )


def test_client_is_paper_safe():
    client = CoinMarketGapAPIClient(
        session=FakeSession(
            FakeResponse({
                "results": rows(),
            })
        )
    )

    result = client.fetch()

    assert result["paper_only"] is True
    assert result[
        "live_order_submitted"
    ] is False
