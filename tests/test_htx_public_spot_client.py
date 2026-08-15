import pytest

from exchanges.htx_public_spot_client import (
    HTXPublicSpotClient,
)


def test_client_has_public_base_url():
    client = HTXPublicSpotClient()

    assert client.base_url == (
        "https://api.huobi.pro"
    )


def test_normalizes_ccxt_symbol():
    client = HTXPublicSpotClient()

    assert client.normalize_symbol(
        "BTC/USDT"
    ) == "btcusdt"

    assert client.normalize_symbol(
        "btc-usdt"
    ) == "btcusdt"

    assert client.normalize_symbol(
        "BTC_USDT"
    ) == "btcusdt"


def test_symbol_is_required():
    client = HTXPublicSpotClient()

    with pytest.raises(
        ValueError,
        match="symbol is required",
    ):
        client.normalize_symbol("")


def test_order_book_limit_must_be_positive():
    client = HTXPublicSpotClient()

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
            "status": "ok",
            "ch": "market.btcusdt.depth.step0",
            "ts": 1700000001000,
            "tick": {
                "bids": [
                    [63038.5, 0.047],
                ],
                "asks": [
                    [63039.0, 0.070],
                ],
                "ts": 1700000000000,
            },
        }),
    ])

    client = HTXPublicSpotClient(
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
    ] == "btcusdt"

    assert result[
        "bids"
    ] == [
        [63038.5, 0.047],
    ]

    assert result[
        "asks"
    ] == [
        [63039.0, 0.070],
    ]

    assert session.calls[0][
        "url"
    ] == (
        "https://api.huobi.pro"
        "/market/depth"
    )

    assert session.calls[0][
        "params"
    ] == {
        "symbol": "btcusdt",
        "type": "step0",
        "depth": 20,
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

    client = HTXPublicSpotClient(
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
            "status": "error",
            "err-code": "invalid-parameter",
            "err-msg": "invalid symbol",
        }),
    ])

    client = HTXPublicSpotClient(
        session=session,
    )

    result = client.fetch_order_book(
        "BTC/USDT"
    )

    assert result[
        "fetch_complete"
    ] is False


def test_missing_depth_fails_closed():
    session = FakeSession([
        FakeResponse({
            "status": "ok",
            "tick": {},
        }),
    ])

    client = HTXPublicSpotClient(
        session=session,
    )

    result = client.fetch_order_book(
        "BTC/USDT"
    )

    assert result[
        "fetch_complete"
    ] is False
