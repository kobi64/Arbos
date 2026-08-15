import pytest

from exchanges.bingx_public_spot_client import (
    BingXPublicSpotClient,
)


def test_client_has_public_base_url():
    client = BingXPublicSpotClient()

    assert client.base_url


def test_normalizes_ccxt_symbol():
    client = BingXPublicSpotClient()

    assert client.normalize_symbol(
        "BTC/USDT"
    )


def test_symbol_is_required():
    client = BingXPublicSpotClient()

    with pytest.raises(
        ValueError,
        match="symbol is required",
    ):
        client.normalize_symbol("")


def test_order_book_limit_must_be_positive():
    client = BingXPublicSpotClient()

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
            "code": 0,
            "timestamp": 1700000000001,
            "data": {
                "bids": [
                    ["63033.97", "0.004689"],
                ],
                "asks": [
                    ["63038.90", "0.000161"],
                ],
                "ts": 1700000000000,
                "lastUpdateId": 12345,
            },
        }),
    ])

    client = BingXPublicSpotClient(
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
    ] == "BTC-USDT"

    assert result[
        "bids"
    ] == [
        ["63033.97", "0.004689"],
    ]

    assert result[
        "asks"
    ] == [
        ["63038.90", "0.000161"],
    ]

    assert result[
        "timestamp"
    ] == 1700000000000

    assert result[
        "last_update_id"
    ] == 12345

    assert session.calls[0][
        "url"
    ] == (
        "https://open-api.bingx.com"
        "/openApi/spot/v1/market/depth"
    )

    assert session.calls[0][
        "params"
    ] == {
        "symbol": "BTC-USDT",
        "limit": 20,
    }


def test_http_failure_is_fail_closed():
    session = FakeSession([
        FakeResponse(
            {},
            status_code=500,
        ),
    ])

    client = BingXPublicSpotClient(
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
            "code": 100400,
            "msg": "Invalid request",
            "timestamp": 1700000000000,
        }),
    ])

    client = BingXPublicSpotClient(
        session=session,
    )

    result = client.fetch_order_book(
        "BTC/USDT"
    )

    assert result[
        "fetch_complete"
    ] is False


def test_missing_data_fails_closed():
    session = FakeSession([
        FakeResponse({
            "code": 0,
            "timestamp": 1700000000000,
        }),
    ])

    client = BingXPublicSpotClient(
        session=session,
    )

    result = client.fetch_order_book(
        "BTC/USDT"
    )

    assert result[
        "fetch_complete"
    ] is False
