import pytest

from exchanges.okx_public_spot_client import (
    OKXPublicSpotClient,
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
                f"http {self.status_code}"
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
        params=None,
        timeout=None,
    ):
        self.calls.append({
            "url": url,
            "params": params,
            "timeout": timeout,
        })

        return self._response


def test_fetch_instruments_calls_spot_endpoint():
    payload = {
        "code": "0",
        "data": [],
    }

    session = FakeSession(
        FakeResponse(
            payload
        )
    )

    client = OKXPublicSpotClient(
        session=session,
    )

    result = client.fetch_instruments()

    assert result == payload

    assert session.calls == [
        {
            "url": (
                "https://www.okx.com"
                "/api/v5/public/instruments"
            ),
            "params": {
                "instType": "SPOT",
            },
            "timeout": 10.0,
        }
    ]


def test_fetch_order_book_normalizes_symbol():
    payload = {
        "code": "0",
        "data": [],
    }

    session = FakeSession(
        FakeResponse(
            payload
        )
    )

    client = OKXPublicSpotClient(
        session=session,
    )

    result = client.fetch_order_book(
        " btc/usdt ",
        limit=20,
    )

    assert result == payload

    assert session.calls == [
        {
            "url": (
                "https://www.okx.com"
                "/api/v5/market/books"
            ),
            "params": {
                "instId": "BTC-USDT",
                "sz": "20",
            },
            "timeout": 10.0,
        }
    ]


def test_symbol_is_required():
    client = OKXPublicSpotClient(
        session=FakeSession(
            FakeResponse({})
        )
    )

    with pytest.raises(
        ValueError,
        match="symbol is required",
    ):
        client.fetch_order_book("")


def test_limit_must_be_positive():
    client = OKXPublicSpotClient(
        session=FakeSession(
            FakeResponse({})
        )
    )

    with pytest.raises(
        ValueError,
        match="limit must be positive",
    ):
        client.fetch_order_book(
            "BTC/USDT",
            limit=0,
        )


def test_http_failure_is_wrapped():
    client = OKXPublicSpotClient(
        session=FakeSession(
            FakeResponse(
                {},
                status_code=500,
            )
        )
    )

    with pytest.raises(
        RuntimeError,
        match="OKX public request unavailable",
    ):
        client.fetch_instruments()


def test_non_dict_payload_is_rejected():
    client = OKXPublicSpotClient(
        session=FakeSession(
            FakeResponse(
                [],
            )
        )
    )

    with pytest.raises(
        RuntimeError,
        match="OKX public request unavailable",
    ):
        client.fetch_instruments()


def test_timeout_must_be_positive():
    with pytest.raises(
        ValueError,
        match="timeout_seconds must be positive",
    ):
        OKXPublicSpotClient(
            timeout_seconds=0,
        )


def test_client_is_read_only():
    client = OKXPublicSpotClient(
        session=FakeSession(
            FakeResponse({})
        )
    )

    assert client.read_only is True
