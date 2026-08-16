import pytest

from exchanges.binance_public_spot_client import (
    BinancePublicSpotClient,
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
    ):
        self.calls.append({
            "url": url,
            "params": params,
            "timeout": timeout,
        })

        return self.responses.pop(0)


def test_fetch_exchange_info():
    session = FakeSession([
        FakeResponse({
            "timezone": "UTC",
            "symbols": [
                {
                    "symbol": "BTCUSDT",
                    "status": "TRADING",
                    "baseAsset": "BTC",
                    "quoteAsset": "USDT",
                    "isSpotTradingAllowed": True,
                }
            ],
        })
    ])

    client = BinancePublicSpotClient(
        session=session,
    )

    result = client.fetch_exchange_info()

    assert result["timezone"] == "UTC"
    assert result["symbols"][0][
        "symbol"
    ] == "BTCUSDT"

    assert session.calls[0]["url"].endswith(
        "/api/v3/exchangeInfo"
    )


def test_fetch_order_book():
    session = FakeSession([
        FakeResponse({
            "lastUpdateId": 98569939561,
            "bids": [
                [
                    "63043.99000000",
                    "7.78416000",
                ],
            ],
            "asks": [
                [
                    "63044.00000000",
                    "40.98952000",
                ],
            ],
        })
    ])

    client = BinancePublicSpotClient(
        session=session,
    )

    result = client.fetch_order_book(
        "BTCUSDT",
        limit=20,
    )

    assert result[
        "lastUpdateId"
    ] == 98569939561

    assert result["bids"][0][0] == (
        "63043.99000000"
    )

    assert session.calls[0]["params"] == {
        "symbol": "BTCUSDT",
        "limit": 20,
    }


def test_fetch_book_ticker():
    session = FakeSession([
        FakeResponse({
            "symbol": "BTCUSDT",
            "bidPrice": "63043.99000000",
            "bidQty": "7.83416000",
            "askPrice": "63044.00000000",
            "askQty": "40.98952000",
        })
    ])

    client = BinancePublicSpotClient(
        session=session,
    )

    result = client.fetch_book_ticker(
        "BTCUSDT"
    )

    assert result["symbol"] == "BTCUSDT"

    assert result[
        "bidPrice"
    ] == "63043.99000000"

    assert result[
        "askPrice"
    ] == "63044.00000000"

    assert session.calls[0]["url"].endswith(
        "/api/v3/ticker/bookTicker"
    )


def test_symbol_is_required_for_order_book():
    client = BinancePublicSpotClient(
        session=FakeSession([]),
    )

    with pytest.raises(
        ValueError,
        match="symbol is required",
    ):
        client.fetch_order_book("")


def test_symbol_is_required_for_book_ticker():
    client = BinancePublicSpotClient(
        session=FakeSession([]),
    )

    with pytest.raises(
        ValueError,
        match="symbol is required",
    ):
        client.fetch_book_ticker("")


def test_default_base_url_is_binance():
    client = BinancePublicSpotClient(
        session=FakeSession([]),
    )

    assert client.base_url == (
        "https://api.binance.com"
    )


def test_custom_base_url_is_normalized():
    client = BinancePublicSpotClient(
        session=FakeSession([]),
        base_url=(
            "https://example.test/"
        ),
    )

    assert client.base_url == (
        "https://example.test"
    )


def test_timeout_must_be_positive():
    with pytest.raises(
        ValueError,
        match="timeout must be positive",
    ):
        BinancePublicSpotClient(
            session=FakeSession([]),
            timeout=0,
        )
