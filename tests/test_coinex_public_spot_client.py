import pytest

from exchanges.coinex_public_spot_client import (
    CoinExPublicSpotClient,
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
        "code": 0,
        "data": {
            "depth": {
                "asks": [
                    ["63044", "0.03977209"],
                    ["63045", "0.00158618"],
                ],
                "bids": [
                    ["63043", "0.80432751"],
                    ["63042", "0.10088271"],
                ],
                "checksum": 2639840070,
                "last": "63043",
                "updated_at": 1786843279189,
            },
            "is_full": True,
            "market": "BTCUSDT",
        },
        "message": "OK",
    }


def test_fetches_public_order_book():
    session = FakeSession(
        FakeResponse(
            successful_payload()
        )
    )

    client = CoinExPublicSpotClient(
        session=session
    )

    result = client.fetch_order_book(
        "BTC/USDT",
        limit=20,
    )

    assert result["code"] == 0
    assert result["message"] == "OK"

    assert result[
        "data"
    ][
        "market"
    ] == "BTCUSDT"

    assert result[
        "data"
    ][
        "depth"
    ][
        "bids"
    ][0] == [
        "63043",
        "0.80432751",
    ]


def test_normalizes_symbol_for_coinex_api():
    session = FakeSession(
        FakeResponse(
            successful_payload()
        )
    )

    client = CoinExPublicSpotClient(
        session=session
    )

    client.fetch_order_book(
        "BTC/USDT",
        limit=20,
    )

    call = session.calls[0]

    assert call["params"] == {
        "market": "BTCUSDT",
        "limit": 20,
        "interval": "0",
    }


def test_uses_coinex_public_depth_endpoint():
    session = FakeSession(
        FakeResponse(
            successful_payload()
        )
    )

    client = CoinExPublicSpotClient(
        session=session
    )

    client.fetch_order_book(
        "BTC/USDT"
    )

    assert session.calls[0]["url"] == (
        "https://api.coinex.com/"
        "v2/spot/depth"
    )


def test_default_limit_is_20():
    session = FakeSession(
        FakeResponse(
            successful_payload()
        )
    )

    client = CoinExPublicSpotClient(
        session=session
    )

    client.fetch_order_book(
        "BTC/USDT"
    )

    assert session.calls[0][
        "params"
    ]["limit"] == 20


def test_symbol_is_required():
    client = CoinExPublicSpotClient(
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
    client = CoinExPublicSpotClient(
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

    client = CoinExPublicSpotClient(
        session=session
    )

    with pytest.raises(
        RuntimeError,
        match="CoinEx public order book unavailable",
    ):
        client.fetch_order_book(
            "BTC/USDT"
        )
