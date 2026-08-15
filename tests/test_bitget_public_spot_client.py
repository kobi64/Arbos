import pytest

from exchanges.bitget_public_spot_client import (
    BitgetPublicSpotClient,
)


def test_client_has_public_base_url():
    client = BitgetPublicSpotClient()

    assert client.base_url == (
        "https://api.bitget.com"
    )


def test_normalizes_ccxt_symbol():
    client = BitgetPublicSpotClient()

    assert client.normalize_symbol(
        "BTC/USDT"
    ) == "BTCUSDT"

    assert client.normalize_symbol(
        "btc-usdt"
    ) == "BTCUSDT"

    assert client.normalize_symbol(
        "BTC_USDT"
    ) == "BTCUSDT"


def test_symbol_is_required():
    client = BitgetPublicSpotClient()

    with pytest.raises(
        ValueError,
        match="symbol is required",
    ):
        client.normalize_symbol("")


def test_order_book_limit_must_be_positive():
    client = BitgetPublicSpotClient()

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
            "code": "00000",
            "msg": "success",
            "data": {
                "asks": [
                    ["63039.0", "0.070"],
                ],
                "bids": [
                    ["63038.5", "0.047"],
                ],
                "ts": "1700000000000",
            },
        }),
    ])

    client = BitgetPublicSpotClient(
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
        ["63038.5", "0.047"],
    ]

    assert result[
        "asks"
    ] == [
        ["63039.0", "0.070"],
    ]

    assert result[
        "timestamp"
    ] == "1700000000000"

    assert session.calls[0][
        "url"
    ] == (
        "https://api.bitget.com"
        "/api/v2/spot/market/orderbook"
    )

    assert session.calls[0][
        "params"
    ] == {
        "symbol": "BTCUSDT",
        "type": "step0",
        "limit": 20,
    }

    assert result[
        "paper_only"
    ] is True

    assert result[
        "live_order_submitted"
    ] is False


def test_http_failure_is_fail_closed():
    session = FakeSession([
        FakeResponse(
            {},
            status_code=500,
        ),
    ])

    client = BitgetPublicSpotClient(
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


def test_exchange_error_fails_closed():
    session = FakeSession([
        FakeResponse({
            "code": "40017",
            "msg": "invalid symbol",
            "data": None,
        }),
    ])

    result = BitgetPublicSpotClient(
        session=session,
    ).fetch_order_book(
        "BTC/USDT"
    )

    assert result[
        "fetch_complete"
    ] is False


def test_missing_depth_fails_closed():
    session = FakeSession([
        FakeResponse({
            "code": "00000",
            "msg": "success",
            "data": {},
        }),
    ])

    result = BitgetPublicSpotClient(
        session=session,
    ).fetch_order_book(
        "BTC/USDT"
    )

    assert result[
        "fetch_complete"
    ] is False
