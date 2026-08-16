import pytest

from exchanges.mexc_public_spot_client import (
    MexcPublicSpotClient,
)


def test_client_has_public_base_url():
    client = MexcPublicSpotClient()

    assert client.base_url == (
        "https://api.mexc.com"
    )


def test_normalizes_ccxt_symbol():
    client = MexcPublicSpotClient()

    assert client.normalize_symbol(
        "BTC/USDT"
    ) == "BTCUSDT"


def test_normalizes_existing_native_symbol():
    client = MexcPublicSpotClient()

    assert client.normalize_symbol(
        "BTCUSDT"
    ) == "BTCUSDT"


def test_symbol_is_required():
    client = MexcPublicSpotClient()

    with pytest.raises(
        ValueError,
        match="symbol is required",
    ):
        client.normalize_symbol("")


def test_order_book_limit_is_validated():
    client = MexcPublicSpotClient()

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
            "lastUpdateId": 1112416,
            "bids": [
                ["15.00000", "49999.00000"],
            ],
            "asks": [
                ["15.10000", "100.00000"],
            ],
        }),
    ])

    client = MexcPublicSpotClient(
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
        ["15.00000", "49999.00000"],
    ]

    assert result[
        "asks"
    ] == [
        ["15.10000", "100.00000"],
    ]

    assert session.calls[0][
        "url"
    ] == (
        "https://api.mexc.com/api/v3/depth"
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

    client = MexcPublicSpotClient(
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

    client = MexcPublicSpotClient(
        session=session,
    )

    result = client.fetch_order_book(
        "BTC/USDT"
    )

    assert result[
        "fetch_complete"
    ] is False


def test_fetches_exchange_info():
    session = FakeSession([
        FakeResponse({
            "timezone": "UTC",
            "symbols": [
                {
                    "symbol": "BTCUSDT",
                    "status": "1",
                    "baseAsset": "BTC",
                    "quoteAsset": "USDT",
                    "baseAssetPrecision": 8,
                    "quoteAssetPrecision": 8,
                    "quoteAmountPrecision": 8,
                    "baseSizePrecision": "0.000001",
                    "quoteAmountPrecisionMarket": "0.000001",
                    "maxQuoteAmount": "1000000",
                    "isSpotTradingAllowed": True,
                    "orderTypes": [
                        "LIMIT",
                        "MARKET",
                    ],
                }
            ],
        }),
    ])

    client = MexcPublicSpotClient(
        session=session,
    )

    result = client.fetch_exchange_info()

    assert result[
        "fetch_complete"
    ] is True

    assert len(
        result["symbols"]
    ) == 1

    assert result["symbols"][0][
        "symbol"
    ] == "BTCUSDT"

    assert session.calls[0][
        "url"
    ] == (
        "https://api.mexc.com"
        "/api/v3/exchangeInfo"
    )

    assert session.calls[0][
        "params"
    ] is None

    assert result[
        "paper_only"
    ] is True

    assert result[
        "live_order_submitted"
    ] is False


def test_exchange_info_http_failure_is_fail_closed():
    session = FakeSession([
        FakeResponse(
            {},
            status_code=500,
        ),
    ])

    client = MexcPublicSpotClient(
        session=session,
    )

    result = client.fetch_exchange_info()

    assert result[
        "fetch_complete"
    ] is False

    assert result[
        "symbols"
    ] == []

    assert result[
        "paper_only"
    ] is True

    assert result[
        "live_order_submitted"
    ] is False

    assert result["reason"]


def test_exchange_info_symbols_must_be_list():
    session = FakeSession([
        FakeResponse({
            "symbols": {},
        }),
    ])

    client = MexcPublicSpotClient(
        session=session,
    )

    result = client.fetch_exchange_info()

    assert result[
        "fetch_complete"
    ] is False

    assert result[
        "symbols"
    ] == []

    assert result["reason"]
