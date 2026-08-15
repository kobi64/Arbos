import pytest

from exchanges.xt_public_spot_client import (
    XTPublicSpotClient,
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
        self.response = response
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

        return self.response


def successful_payload():
    return {
        "rc": 0,
        "mc": "SUCCESS",
        "ma": [],
        "result": {
            "symbol": "btc_usdt",
            "timestamp": 1700000000000,
            "lastUpdateId": 12345,
            "bids": [
                ["63094.99", "23.31624"],
                ["63094.97", "0.35580"],
            ],
            "asks": [
                ["63095.00", "12.14463"],
                ["63095.09", "0.43631"],
            ],
        },
    }


def test_fetches_public_order_book():
    session = FakeSession(
        FakeResponse(
            successful_payload()
        )
    )

    client = XTPublicSpotClient(
        session=session
    )

    result = client.fetch_order_book(
        "BTC/USDT",
        limit=20,
    )

    assert result["rc"] == 0
    assert result["mc"] == "SUCCESS"

    assert result["result"][
        "symbol"
    ] == "btc_usdt"

    assert result["result"][
        "bids"
    ][0] == [
        "63094.99",
        "23.31624",
    ]

    assert result["result"][
        "asks"
    ][0] == [
        "63095.00",
        "12.14463",
    ]


def test_normalizes_symbol_for_xt_api():
    session = FakeSession(
        FakeResponse(
            successful_payload()
        )
    )

    client = XTPublicSpotClient(
        session=session
    )

    client.fetch_order_book(
        "BTC/USDT",
        limit=20,
    )

    call = session.calls[0]

    assert call["params"] == {
        "symbol": "btc_usdt",
        "limit": 20,
    }


def test_uses_xt_public_depth_endpoint():
    session = FakeSession(
        FakeResponse(
            successful_payload()
        )
    )

    client = XTPublicSpotClient(
        session=session
    )

    client.fetch_order_book(
        "BTC/USDT"
    )

    assert session.calls[0]["url"] == (
        "https://sapi.xt.com/"
        "v4/public/depth"
    )


def test_default_limit_is_20():
    session = FakeSession(
        FakeResponse(
            successful_payload()
        )
    )

    client = XTPublicSpotClient(
        session=session
    )

    client.fetch_order_book(
        "BTC/USDT"
    )

    assert session.calls[0][
        "params"
    ]["limit"] == 20


def test_symbol_is_required():
    client = XTPublicSpotClient(
        session=FakeSession(
            FakeResponse(
                successful_payload()
            )
        )
    )

    with pytest.raises(
        ValueError,
        match="symbol is required",
    ):
        client.fetch_order_book("")


def test_invalid_limit_is_rejected():
    client = XTPublicSpotClient(
        session=FakeSession(
            FakeResponse(
                successful_payload()
            )
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


def test_failed_request_fails_closed():
    session = FakeSession(
        FakeResponse(
            {},
            status_code=500,
        )
    )

    client = XTPublicSpotClient(
        session=session
    )

    with pytest.raises(
        RuntimeError,
        match="XT public order book unavailable",
    ):
        client.fetch_order_book(
            "BTC/USDT"
        )
