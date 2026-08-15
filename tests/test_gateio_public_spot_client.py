import pytest

from exchanges.gateio_public_spot_client import (
    GateIOPublicSpotClient,
)


def test_client_has_public_base_url():
    client = GateIOPublicSpotClient()

    assert client.base_url == "https://api.gateio.ws"


def test_normalizes_ccxt_symbol():
    client = GateIOPublicSpotClient()

    assert client.normalize_symbol(
        "BTC/USDT"
    ) == "BTC_USDT"

    assert client.normalize_symbol(
        "btc-usdt"
    ) == "BTC_USDT"

    assert client.normalize_symbol(
        "BTC_USDT"
    ) == "BTC_USDT"


def test_symbol_is_required():
    client = GateIOPublicSpotClient()

    with pytest.raises(
        ValueError,
        match="symbol is required",
    ):
        client.normalize_symbol("")


def test_order_book_limit_must_be_positive():
    client = GateIOPublicSpotClient()

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
            "id": 123456,
            "current": 1700000001000,
            "update": 1700000000000,
            "asks": [
                ["63039.0", "0.070"],
            ],
            "bids": [
                ["63038.5", "0.047"],
            ],
        }),
    ])

    client = GateIOPublicSpotClient(
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
    ] == "BTC_USDT"

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

    assert session.calls[0][
        "url"
    ] == (
        "https://api.gateio.ws"
        "/api/v4/spot/order_book"
    )

    assert session.calls[0][
        "params"
    ] == {
        "currency_pair": "BTC_USDT",
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

    client = GateIOPublicSpotClient(
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


def test_malformed_payload_fails_closed():
    session = FakeSession([
        FakeResponse([]),
    ])

    client = GateIOPublicSpotClient(
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
            "id": 123456,
            "current": 1700000001000,
        }),
    ])

    client = GateIOPublicSpotClient(
        session=session,
    )

    result = client.fetch_order_book(
        "BTC/USDT"
    )

    assert result[
        "fetch_complete"
    ] is False
