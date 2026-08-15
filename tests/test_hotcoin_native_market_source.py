from exchanges.hotcoin_native_market_source import (
    HotcoinNativeMarketSource,
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


def test_fetches_hotcoin_native_catalogue():
    session = FakeSession([
        FakeResponse({
            "code": 200,
            "msg": "成功",
            "data": [
                {
                    "baseCurrency": "btc",
                    "quoteCurrency": "usdt",
                    "pricePrecision": 2,
                    "amountPrecision": 5,
                    "symbolPartition": "main",
                    "symbol": "btc_usdt",
                    "state": "enable",
                    "minOrderAmount": 15.0,
                },
                {
                    "baseCurrency": "eth",
                    "quoteCurrency": "btc",
                    "pricePrecision": 5,
                    "amountPrecision": 4,
                    "symbolPartition": "main",
                    "symbol": "eth_btc",
                    "state": "enable",
                    "minOrderAmount": 0.0001,
                },
            ],
        }),
    ])

    source = HotcoinNativeMarketSource(
        session=session,
    )

    result = source.fetch()

    assert result[
        "fetch_complete"
    ] is True

    assert result[
        "exchange_id"
    ] == "hotcoin"

    assert result[
        "symbols"
    ] == [
        "BTC/USDT",
        "ETH/BTC",
    ]

    assert result[
        "market_count"
    ] == 2

    assert session.calls[0][
        "url"
    ] == (
        "https://api.hotcoinfin.com"
        "/v1/common/symbols"
    )


def test_preserves_hotcoin_market_metadata():
    session = FakeSession([
        FakeResponse({
            "code": 200,
            "data": [
                {
                    "baseCurrency": "btc",
                    "quoteCurrency": "usdt",
                    "pricePrecision": 2,
                    "amountPrecision": 5,
                    "symbolPartition": "main",
                    "symbol": "btc_usdt",
                    "state": "enable",
                    "minOrderAmount": 15.0,
                },
            ],
        }),
    ])

    result = HotcoinNativeMarketSource(
        session=session,
    ).fetch()

    market = result[
        "markets"
    ][0]

    assert market[
        "symbol"
    ] == "BTC/USDT"

    assert market[
        "status"
    ] == "TRADING"

    assert market[
        "price_precision"
    ] == 2

    assert market[
        "amount_precision"
    ] == 5

    assert market[
        "minimum_value"
    ] == 15.0

    assert market[
        "native_symbol"
    ] == "btc_usdt"


def test_disabled_market_is_suspended():
    session = FakeSession([
        FakeResponse({
            "code": 200,
            "data": [
                {
                    "baseCurrency": "abc",
                    "quoteCurrency": "usdt",
                    "symbol": "abc_usdt",
                    "state": "disable",
                },
            ],
        }),
    ])

    result = HotcoinNativeMarketSource(
        session=session,
    ).fetch()

    assert result[
        "markets"
    ][0][
        "status"
    ] == "SUSPENDED"


def test_exchange_error_fails_closed():
    session = FakeSession([
        FakeResponse({
            "code": 10170,
            "msg": "API未开放",
        }),
    ])

    result = HotcoinNativeMarketSource(
        session=session,
    ).fetch()

    assert result[
        "fetch_complete"
    ] is False

    assert result[
        "symbols"
    ] == []

    assert result[
        "markets"
    ] == []


def test_http_failure_fails_closed():
    session = FakeSession([
        FakeResponse(
            {},
            status_code=500,
        ),
    ])

    result = HotcoinNativeMarketSource(
        session=session,
    ).fetch()

    assert result[
        "fetch_complete"
    ] is False

    assert result[
        "market_count"
    ] == 0
