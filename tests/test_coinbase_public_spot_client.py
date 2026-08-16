import pytest

from exchanges.coinbase_public_spot_client import (
    CoinbasePublicSpotClient,
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
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []

    def get(
        self,
        url,
        params=None,
        timeout=None,
        headers=None,
    ):
        self.calls.append({
            "url": url,
            "params": params,
            "timeout": timeout,
            "headers": headers,
        })

        return self.responses.pop(0)


def test_fetch_products():
    session = FakeSession([
        FakeResponse([
            {
                "id": "BTC-USD",
                "base_currency": "BTC",
                "quote_currency": "USD",
                "status": "online",
            }
        ])
    ])

    client = CoinbasePublicSpotClient(
        session=session,
    )

    result = client.fetch_products()

    assert result[0]["id"] == "BTC-USD"

    assert session.calls[0]["url"].endswith(
        "/products"
    )


def test_fetch_order_book():
    session = FakeSession([
        FakeResponse({
            "sequence": 123456,
            "bids": [
                ["62990.24", "0.10232494", 6],
            ],
            "asks": [
                ["62990.25", "0.10000000", 2],
            ],
        })
    ])

    client = CoinbasePublicSpotClient(
        session=session,
    )

    result = client.fetch_order_book(
        "BTC-USD",
        level=2,
    )

    assert result["sequence"] == 123456

    assert session.calls[0]["url"].endswith(
        "/products/BTC-USD/book"
    )

    assert session.calls[0]["params"] == {
        "level": 2,
    }


def test_fetch_ticker():
    session = FakeSession([
        FakeResponse({
            "ask": "62990.25",
            "bid": "62990.24",
            "price": "62990.25",
        })
    ])

    client = CoinbasePublicSpotClient(
        session=session,
    )

    result = client.fetch_ticker(
        "BTC-USD"
    )

    assert result["bid"] == "62990.24"
    assert result["ask"] == "62990.25"

    assert session.calls[0]["url"].endswith(
        "/products/BTC-USD/ticker"
    )


def test_fetch_currencies():
    session = FakeSession([
        FakeResponse([
            {
                "id": "BTC",
                "status": "online",
                "supported_networks": [],
            }
        ])
    ])

    client = CoinbasePublicSpotClient(
        session=session,
    )

    result = client.fetch_currencies()

    assert result[0]["id"] == "BTC"

    assert session.calls[0]["url"].endswith(
        "/currencies"
    )


def test_product_id_is_normalized():
    session = FakeSession([
        FakeResponse({})
    ])

    client = CoinbasePublicSpotClient(
        session=session,
    )

    client.fetch_ticker(
        " btc/usd "
    )

    assert session.calls[0]["url"].endswith(
        "/products/BTC-USD/ticker"
    )


def test_product_id_is_required():
    client = CoinbasePublicSpotClient(
        session=FakeSession([]),
    )

    with pytest.raises(
        ValueError,
        match="product_id is required",
    ):
        client.fetch_order_book("")


def test_default_base_url():
    client = CoinbasePublicSpotClient(
        session=FakeSession([]),
    )

    assert client.base_url == (
        "https://api.exchange.coinbase.com"
    )


def test_custom_base_url_is_normalized():
    client = CoinbasePublicSpotClient(
        session=FakeSession([]),
        base_url="https://example.test/",
    )

    assert client.base_url == (
        "https://example.test"
    )


def test_timeout_must_be_positive():
    with pytest.raises(
        ValueError,
        match="timeout must be positive",
    ):
        CoinbasePublicSpotClient(
            session=FakeSession([]),
            timeout=0,
        )
