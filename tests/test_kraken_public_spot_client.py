import pytest

from exchanges.kraken_public_spot_client import (
    KrakenPublicSpotClient,
)


def test_client_has_public_base_url():
    client = KrakenPublicSpotClient()

    assert client.base_url


def test_normalizes_ccxt_symbol():
    client = KrakenPublicSpotClient()

    assert client.normalize_symbol(
        "BTC/USDT"
    )


def test_symbol_is_required():
    client = KrakenPublicSpotClient()

    with pytest.raises(
        ValueError,
        match="symbol is required",
    ):
        client.normalize_symbol("")


def test_order_book_limit_must_be_positive():
    client = KrakenPublicSpotClient()

    with pytest.raises(
        ValueError,
        match="limit must be positive",
    ):
        client.fetch_order_book(
            "BTC/USDT",
            limit=0,
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
        responses,
    ):
        self._responses = list(
            responses
        )
        self.calls = []

    def get(
        self,
        url,
        params=None,
        timeout=None,
    ):
        self.calls.append({
            "url": url,
            "params": params,
            "timeout": timeout,
        })

        return self._responses.pop(0)


def test_fetches_order_book():
    session = FakeSession([
        FakeResponse({
            "error": [],
            "result": {
                "XBTUSDT": {
                    "asks": [
                        ["63039.0", "0.070", 1700000001],
                    ],
                    "bids": [
                        ["63038.5", "0.047", 1700000000],
                    ],
                },
            },
        }),
    ])

    client = KrakenPublicSpotClient(
        session=session,
    )

    result = client.fetch_order_book(
        "BTC/USDT",
        limit=20,
    )

    assert result[
        "fetch_complete"
    ] is True

    assert result[
        "symbol"
    ] == "BTCUSDT"

    assert result[
        "bids"
    ] == [
        ["63038.5", "0.047", 1700000000],
    ]

    assert result[
        "asks"
    ] == [
        ["63039.0", "0.070", 1700000001],
    ]

    assert session.calls[0][
        "url"
    ] == (
        "https://api.kraken.com"
        "/0/public/Depth"
    )

    assert session.calls[0][
        "params"
    ] == {
        "pair": "BTCUSDT",
        "count": 20,
    }


def test_http_failure_is_fail_closed():
    session = FakeSession([
        FakeResponse(
            {},
            status_code=500,
        ),
    ])

    client = KrakenPublicSpotClient(
        session=session,
    )

    result = client.fetch_order_book(
        "BTC/USDT"
    )

    assert result[
        "fetch_complete"
    ] is False

    assert result[
        "bids"
    ] == []

    assert result[
        "asks"
    ] == []

    assert result[
        "paper_only"
    ] is True

    assert result[
        "live_order_submitted"
    ] is False


def test_exchange_error_fails_closed():
    session = FakeSession([
        FakeResponse({
            "error": [
                "EQuery:Unknown asset pair"
            ],
            "result": {},
        }),
    ])

    client = KrakenPublicSpotClient(
        session=session,
    )

    result = client.fetch_order_book(
        "BTC/USDT"
    )

    assert result[
        "fetch_complete"
    ] is False


def test_empty_result_fails_closed():
    session = FakeSession([
        FakeResponse({
            "error": [],
            "result": {},
        }),
    ])

    client = KrakenPublicSpotClient(
        session=session,
    )

    result = client.fetch_order_book(
        "BTC/USDT"
    )

    assert result[
        "fetch_complete"
    ] is False
