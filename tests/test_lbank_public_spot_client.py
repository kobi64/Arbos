import pytest

from exchanges.lbank_public_spot_client import (
    LBankPublicSpotClient,
)


def test_client_has_public_base_url():
    client = LBankPublicSpotClient()

    assert client.base_url


def test_normalizes_ccxt_symbol():
    client = LBankPublicSpotClient()

    assert client.normalize_symbol(
        "BTC/USDT"
    )


def test_symbol_is_required():
    client = LBankPublicSpotClient()

    with pytest.raises(
        ValueError,
        match="symbol is required",
    ):
        client.normalize_symbol("")


def test_order_book_limit_must_be_positive():
    client = LBankPublicSpotClient()

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
            "result": "true",
            "msg": "Success",
            "data": {
                "asks": [
                    ["63144.63", "2.04678"],
                ],
                "bids": [
                    ["63144.62", "5.64875"],
                ],
                "timestamp": 1700000000000,
            },
            "error_code": 0,
            "ts": 1700000000000,
        }),
    ])

    client = LBankPublicSpotClient(
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
    ] == "btc_usdt"

    assert result[
        "bids"
    ] == [
        ["63144.62", "5.64875"],
    ]

    assert result[
        "asks"
    ] == [
        ["63144.63", "2.04678"],
    ]

    assert result[
        "timestamp"
    ] == 1700000000000

    assert session.calls[0][
        "url"
    ] == (
        "https://api.lbkex.com"
        "/v2/depth.do"
    )

    assert session.calls[0][
        "params"
    ] == {
        "symbol": "btc_usdt",
        "size": 20,
    }


def test_order_book_http_failure_is_fail_closed():
    session = FakeSession([
        FakeResponse(
            {},
            status_code=500,
        ),
    ])

    client = LBankPublicSpotClient(
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


def test_missing_depth_data_fails_closed():
    session = FakeSession([
        FakeResponse({
            "result": "true",
            "msg": "Success",
            "error_code": 0,
            "ts": 1700000000000,
        }),
    ])

    client = LBankPublicSpotClient(
        session=session,
    )

    result = client.fetch_order_book(
        "BTC/USDT"
    )

    assert result[
        "fetch_complete"
    ] is False


def test_exchange_error_fails_closed():
    session = FakeSession([
        FakeResponse({
            "result": "false",
            "msg": "Invalid symbol",
            "error_code": 10007,
        }),
    ])

    client = LBankPublicSpotClient(
        session=session,
    )

    result = client.fetch_order_book(
        "BTC/USDT"
    )

    assert result[
        "fetch_complete"
    ] is False


def test_fetches_currency_pairs():
    session = FakeSession([
        FakeResponse({
            "msg": "Success",
            "result": "true",
            "data": [
                "btc_usdt",
                "eth_usdt",
                "trx_eth",
                "dgb_usdt",
            ],
            "error_code": 0,
            "ts": 1700000000000,
        }),
    ])

    client = LBankPublicSpotClient(
        session=session,
    )

    result = client.fetch_markets()

    assert result[
        "fetch_complete"
    ] is True

    assert result[
        "markets"
    ] == [
        "btc_usdt",
        "eth_usdt",
        "trx_eth",
        "dgb_usdt",
    ]

    assert result[
        "market_count"
    ] == 4

    assert result[
        "paper_only"
    ] is True

    assert result[
        "live_order_submitted"
    ] is False

    assert session.calls[0][
        "url"
    ] == (
        "https://api.lbkex.com"
        "/v2/currencyPairs.do"
    )

    assert session.calls[0][
        "params"
    ] is None


def test_currency_pairs_http_failure_is_fail_closed():
    session = FakeSession([
        FakeResponse(
            {},
            status_code=500,
        ),
    ])

    client = LBankPublicSpotClient(
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


def test_currency_pairs_payload_must_be_dictionary():
    session = FakeSession([
        FakeResponse([]),
    ])

    client = LBankPublicSpotClient(
        session=session,
    )

    result = client.fetch_markets()

    assert result[
        "fetch_complete"
    ] is False

    assert result[
        "markets"
    ] == []


def test_currency_pairs_exchange_error_fails_closed():
    session = FakeSession([
        FakeResponse({
            "result": "false",
            "msg": "Exchange error",
            "error_code": 10000,
        }),
    ])

    client = LBankPublicSpotClient(
        session=session,
    )

    result = client.fetch_markets()

    assert result[
        "fetch_complete"
    ] is False

    assert result[
        "markets"
    ] == []


def test_currency_pairs_data_must_be_list():
    session = FakeSession([
        FakeResponse({
            "msg": "Success",
            "result": "true",
            "data": {},
            "error_code": 0,
            "ts": 1700000000000,
        }),
    ])

    client = LBankPublicSpotClient(
        session=session,
    )

    result = client.fetch_markets()

    assert result[
        "fetch_complete"
    ] is False

    assert result[
        "markets"
    ] == []


def test_currency_pairs_preserve_native_symbols():
    session = FakeSession([
        FakeResponse({
            "msg": "Success",
            "result": "true",
            "data": [
                "btc_usdt",
                "trx_eth",
                "btcv_btc",
            ],
            "error_code": 0,
            "ts": 1700000000000,
        }),
    ])

    client = LBankPublicSpotClient(
        session=session,
    )

    result = client.fetch_markets()

    assert result[
        "markets"
    ] == [
        "btc_usdt",
        "trx_eth",
        "btcv_btc",
    ]
