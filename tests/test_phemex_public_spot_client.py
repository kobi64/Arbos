import pytest

from exchanges.phemex_public_spot_client import (
    PhemexPublicSpotClient,
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


def valid_payload():
    return {
        "error": None,
        "id": 0,
        "result": {
            "book": {
                "asks": [
                    [
                        6305469000000,
                        5966600,
                    ],
                ],
                "bids": [
                    [
                        6305468000000,
                        4264100,
                    ],
                ],
            },
            "depth": 30,
            "sequence": 40398521651,
            "symbol": "sBTCUSDT",
            "timestamp": 1786845356093279821,
            "type": "snapshot",
        },
    }


def test_fetch_order_book_calls_phemex_spot_endpoint():
    session = FakeSession(
        FakeResponse(
            valid_payload()
        )
    )

    client = PhemexPublicSpotClient(
        session=session,
    )

    result = client.fetch_order_book(
        "BTC/USDT"
    )

    assert result["result"]["symbol"] == (
        "sBTCUSDT"
    )

    assert session.calls == [
        {
            "url": (
                "https://api.phemex.com"
                "/md/orderbook"
            ),
            "params": {
                "symbol": "sBTCUSDT",
            },
            "timeout": 10.0,
        }
    ]


def test_symbol_is_normalized_to_spot_native_symbol():
    session = FakeSession(
        FakeResponse(
            valid_payload()
        )
    )

    client = PhemexPublicSpotClient(
        session=session,
    )

    client.fetch_order_book(
        " btc/usdt "
    )

    assert session.calls[0][
        "params"
    ]["symbol"] == "sBTCUSDT"


def test_existing_native_spot_symbol_is_preserved():
    session = FakeSession(
        FakeResponse(
            valid_payload()
        )
    )

    client = PhemexPublicSpotClient(
        session=session,
    )

    client.fetch_order_book(
        "sBTCUSDT"
    )

    assert session.calls[0][
        "params"
    ]["symbol"] == "sBTCUSDT"


def test_plain_perpetual_style_symbol_is_not_used_directly():
    session = FakeSession(
        FakeResponse(
            valid_payload()
        )
    )

    client = PhemexPublicSpotClient(
        session=session,
    )

    client.fetch_order_book(
        "BTCUSDT"
    )

    assert session.calls[0][
        "params"
    ]["symbol"] == "sBTCUSDT"


def test_symbol_is_required():
    client = PhemexPublicSpotClient(
        session=FakeSession(
            FakeResponse(
                valid_payload()
            )
        )
    )

    with pytest.raises(
        ValueError,
        match="symbol is required",
    ):
        client.fetch_order_book("")


def test_timeout_must_be_positive():
    with pytest.raises(
        ValueError,
        match="timeout_seconds must be positive",
    ):
        PhemexPublicSpotClient(
            timeout_seconds=0,
        )


def test_http_failure_is_wrapped():
    session = FakeSession(
        FakeResponse(
            {},
            status_code=500,
        )
    )

    client = PhemexPublicSpotClient(
        session=session,
    )

    with pytest.raises(
        RuntimeError,
        match="Phemex public spot order book unavailable",
    ):
        client.fetch_order_book(
            "BTC/USDT"
        )


def test_client_is_read_only():
    client = PhemexPublicSpotClient(
        session=FakeSession(
            FakeResponse(
                valid_payload()
            )
        )
    )

    assert client.read_only is True


def test_fetch_products_calls_public_products_endpoint():
    payload = {
        "code": 0,
        "data": {
            "currencies": [],
            "products": [],
        },
    }

    session = FakeSession(
        FakeResponse(
            payload
        )
    )

    client = PhemexPublicSpotClient(
        session=session,
    )

    result = client.fetch_products()

    assert result == payload

    assert session.calls == [
        {
            "url": (
                "https://api.phemex.com"
                "/public/products"
            ),
            "params": None,
            "timeout": 10.0,
        }
    ]


def test_fetch_products_http_failure_is_wrapped():
    session = FakeSession(
        FakeResponse(
            {},
            status_code=500,
        )
    )

    client = PhemexPublicSpotClient(
        session=session,
    )

    with pytest.raises(
        RuntimeError,
        match="Phemex public products unavailable",
    ):
        client.fetch_products()
