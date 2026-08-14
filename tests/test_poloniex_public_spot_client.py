import pytest

from exchanges.poloniex_public_spot_client import (
    PoloniexPublicSpotClient,
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


def test_fetches_markets():
    session = FakeSession([
        FakeResponse([
            {
                "symbol": "BTC_USDT",
                "baseCurrencyName": "BTC",
                "quoteCurrencyName": "USDT",
                "state": "NORMAL",
            },
        ]),
    ])

    client = PoloniexPublicSpotClient(
        session=session,
    )

    result = client.fetch_markets()

    assert result[
        "fetch_complete"
    ] is True

    assert result[
        "markets"
    ][0][
        "symbol"
    ] == "BTC_USDT"

    assert session.calls[0][
        "url"
    ] == (
        "https://api.poloniex.com/markets"
    )


def test_fetches_currency_v2_metadata():
    session = FakeSession([
        FakeResponse([
            {
                "id": 1,
                "coin": "USDT",
                "delisted": False,
                "tradeEnable": True,
                "name": "Tether",
                "networkList": [
                    {
                        "coin": "USDTTRON",
                        "name": "Tron",
                        "blockchain": "TRX",
                        "withdrawalEnable": True,
                        "depositEnable": True,
                        "withdrawMin": "10",
                        "withdrawFee": "1",
                        "minConfirm": 20,
                        "contractAddress": (
                            "TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t"
                        ),
                    },
                ],
            },
        ]),
    ])

    client = PoloniexPublicSpotClient(
        session=session,
    )

    result = client.fetch_currencies()

    assert result[
        "fetch_complete"
    ] is True

    assert result[
        "currencies"
    ][0][
        "coin"
    ] == "USDT"

    network = result[
        "currencies"
    ][0][
        "networkList"
    ][0]

    assert network[
        "withdrawalEnable"
    ] is True

    assert network[
        "depositEnable"
    ] is True

    assert network[
        "contractAddress"
    ] is not None

    assert session.calls[0][
        "url"
    ] == (
        "https://api.poloniex.com/v2/currencies"
    )


def test_timeout_must_be_positive():
    with pytest.raises(
        ValueError,
        match="timeout_seconds must be positive",
    ):
        PoloniexPublicSpotClient(
            session=FakeSession([]),
            timeout_seconds=0,
        )


def test_http_failure_is_fail_closed():
    session = FakeSession([
        FakeResponse(
            {},
            status_code=500,
        ),
    ])

    client = PoloniexPublicSpotClient(
        session=session,
    )

    result = client.fetch_markets()

    assert result[
        "fetch_complete"
    ] is False

    assert result[
        "paper_only"
    ] is True

    assert result[
        "live_order_submitted"
    ] is False


def test_client_is_paper_safe():
    session = FakeSession([
        FakeResponse([]),
    ])

    client = PoloniexPublicSpotClient(
        session=session,
    )

    result = client.fetch_markets()

    assert result[
        "paper_only"
    ] is True

    assert result[
        "live_order_submitted"
    ] is False


def test_fetches_order_book():
    session = FakeSession([
        FakeResponse({
            "time": 1234567890,
            "scale": "-1",
            "asks": [
                "0.101",
                "50",
                "0.102",
                "100",
            ],
            "bids": [
                "0.100",
                "75",
                "0.099",
                "125",
            ],
        }),
    ])

    client = PoloniexPublicSpotClient(
        session=session,
    )

    result = client.fetch_order_book(
        symbol="FIR_USDT",
        limit=20,
    )

    assert result[
        "fetch_complete"
    ] is True

    assert result[
        "symbol"
    ] == "FIR_USDT"

    assert result[
        "asks"
    ] == [
        "0.101",
        "50",
        "0.102",
        "100",
    ]

    assert result[
        "bids"
    ] == [
        "0.100",
        "75",
        "0.099",
        "125",
    ]

    assert session.calls[0][
        "url"
    ] == (
        "https://api.poloniex.com/"
        "markets/FIR_USDT/orderBook"
    )

    assert session.calls[0][
        "params"
    ] == {
        "limit": 20,
    }


def test_order_book_symbol_is_required():
    client = PoloniexPublicSpotClient(
        session=FakeSession([]),
    )

    with pytest.raises(
        ValueError,
        match="symbol is required",
    ):
        client.fetch_order_book(
            symbol="",
        )


def test_order_book_limit_must_be_positive():
    client = PoloniexPublicSpotClient(
        session=FakeSession([]),
    )

    with pytest.raises(
        ValueError,
        match="limit must be positive",
    ):
        client.fetch_order_book(
            symbol="BTC_USDT",
            limit=0,
        )
