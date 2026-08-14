import pytest

from exchanges.ourbit_public_spot_client import (
    OurbitPublicSpotClient,
)


def test_client_has_public_base_url():
    client = OurbitPublicSpotClient()

    assert client.base_url


def test_normalizes_ccxt_symbol():
    client = OurbitPublicSpotClient()

    assert client.normalize_symbol(
        "BTC/USDT"
    ) == "BTCUSDT"


def test_normalizes_native_symbol():
    client = OurbitPublicSpotClient()

    assert client.normalize_symbol(
        "BTCUSDT"
    ) == "BTCUSDT"


def test_symbol_is_required():
    client = OurbitPublicSpotClient()

    with pytest.raises(
        ValueError,
        match="symbol is required",
    ):
        client.normalize_symbol("")


def test_order_book_limit_must_be_positive():
    client = OurbitPublicSpotClient()

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
            "lastUpdateId": 12345,
            "bids": [
                ["62895.79", "6.319350"],
            ],
            "asks": [
                ["62895.80", "4.504951"],
            ],
            "timestamp": 1700000000000,
        }),
    ])

    client = OurbitPublicSpotClient(
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
        ["62895.79", "6.319350"],
    ]

    assert result[
        "asks"
    ] == [
        ["62895.80", "4.504951"],
    ]

    assert result[
        "timestamp"
    ] == 1700000000000

    assert session.calls[0][
        "url"
    ] == (
        "https://api.ourbit.com"
        "/api/v3/depth"
    )

    assert session.calls[0][
        "params"
    ] == {
        "symbol": "BTCUSDT",
        "limit": 20,
    }


def test_order_book_http_failure_is_fail_closed():
    session = FakeSession([
        FakeResponse(
            {},
            status_code=500,
        ),
    ])

    client = OurbitPublicSpotClient(
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


def test_order_book_payload_must_be_dictionary():
    session = FakeSession([
        FakeResponse([]),
    ])

    client = OurbitPublicSpotClient(
        session=session,
    )

    result = client.fetch_order_book(
        "BTC/USDT"
    )

    assert result[
        "fetch_complete"
    ] is False
