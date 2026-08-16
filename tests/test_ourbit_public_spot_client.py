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


def test_fetches_exchange_info_markets():
    session = FakeSession([
        FakeResponse({
            "timezone": "CST",
            "serverTime": 1700000000000,
            "rateLimits": [],
            "exchangeFilters": [],
            "symbols": [
                {
                    "symbol": "BTCUSDT",
                    "status": "ENABLED",
                    "baseAsset": "BTC",
                    "baseAssetPrecision": 6,
                    "quoteAsset": "USDT",
                    "quotePrecision": 2,
                    "quoteAssetPrecision": 2,
                    "isSpotTradingAllowed": False,
                    "permissions": ["SPOT"],
                    "filters": [],
                },
                {
                    "symbol": "ETHUSDT",
                    "status": "ENABLED",
                    "baseAsset": "ETH",
                    "baseAssetPrecision": 5,
                    "quoteAsset": "USDT",
                    "quotePrecision": 2,
                    "quoteAssetPrecision": 2,
                    "isSpotTradingAllowed": False,
                    "permissions": ["SPOT"],
                    "filters": [],
                },
            ],
        }),
    ])

    client = OurbitPublicSpotClient(
        session=session,
    )

    result = client.fetch_markets()

    assert result[
        "fetch_complete"
    ] is True

    assert result[
        "market_count"
    ] == 2

    assert result[
        "markets"
    ][0]["symbol"] == "BTCUSDT"

    assert result[
        "markets"
    ][0]["baseAsset"] == "BTC"

    assert result[
        "markets"
    ][0]["quoteAsset"] == "USDT"

    assert result[
        "markets"
    ][0]["status"] == "ENABLED"

    assert result[
        "paper_only"
    ] is True

    assert result[
        "live_order_submitted"
    ] is False

    assert session.calls[0][
        "url"
    ] == (
        "https://api.ourbit.com"
        "/api/v3/exchangeInfo"
    )

    assert session.calls[0][
        "params"
    ] is None


def test_exchange_info_http_failure_is_fail_closed():
    session = FakeSession([
        FakeResponse(
            {},
            status_code=500,
        ),
    ])

    client = OurbitPublicSpotClient(
        session=session,
    )

    result = client.fetch_markets()

    assert result[
        "fetch_complete"
    ] is False

    assert result[
        "markets"
    ] == []

    assert result[
        "market_count"
    ] == 0

    assert result[
        "paper_only"
    ] is True

    assert result[
        "live_order_submitted"
    ] is False


def test_exchange_info_payload_must_be_dictionary():
    session = FakeSession([
        FakeResponse([]),
    ])

    client = OurbitPublicSpotClient(
        session=session,
    )

    result = client.fetch_markets()

    assert result[
        "fetch_complete"
    ] is False

    assert result[
        "markets"
    ] == []


def test_exchange_info_symbols_must_be_list():
    session = FakeSession([
        FakeResponse({
            "timezone": "CST",
            "symbols": {},
        }),
    ])

    client = OurbitPublicSpotClient(
        session=session,
    )

    result = client.fetch_markets()

    assert result[
        "fetch_complete"
    ] is False

    assert result[
        "markets"
    ] == []

    assert result[
        "market_count"
    ] == 0


def test_exchange_info_preserves_native_market_metadata():
    market = {
        "symbol": "QNTUSDT",
        "status": "ENABLED",
        "baseAsset": "QNT",
        "baseAssetPrecision": 3,
        "quoteAsset": "USDT",
        "quotePrecision": 1,
        "quoteAssetPrecision": 1,
        "orderTypes": [
            "LIMIT",
            "MARKET",
            "LIMIT_MAKER",
        ],
        "isSpotTradingAllowed": False,
        "isMarginTradingAllowed": False,
        "permissions": ["SPOT"],
        "filters": [],
    }

    session = FakeSession([
        FakeResponse({
            "timezone": "CST",
            "serverTime": 1700000000000,
            "symbols": [market],
        }),
    ])

    client = OurbitPublicSpotClient(
        session=session,
    )

    result = client.fetch_markets()

    assert result[
        "markets"
    ] == [market]


def test_exchange_info_empty_catalogue_is_complete():
    session = FakeSession([
        FakeResponse({
            "timezone": "CST",
            "serverTime": 1700000000000,
            "symbols": [],
        }),
    ])

    client = OurbitPublicSpotClient(
        session=session,
    )

    result = client.fetch_markets()

    assert result[
        "fetch_complete"
    ] is True

    assert result[
        "markets"
    ] == []

    assert result[
        "market_count"
    ] == 0
