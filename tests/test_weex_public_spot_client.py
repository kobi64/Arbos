import pytest

from exchanges.weex_public_spot_client import (
    WeexPublicSpotClient,
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


def test_fetches_api_spot_symbols():
    session = FakeSession([
        FakeResponse([
            "BTCUSDT",
            "ETHUSDT",
            "SOLUSDT",
        ]),
    ])

    client = WeexPublicSpotClient(
        session=session,
        timeout_seconds=15,
    )

    result = client.fetch_symbols()

    assert result[
        "fetch_complete"
    ] is True

    assert result[
        "symbols"
    ] == [
        "BTCUSDT",
        "ETHUSDT",
        "SOLUSDT",
    ]

    assert session.calls[0][
        "url"
    ] == (
        "https://api-spot.weex.com/"
        "api/v3/apiTradingSymbols"
    )


def test_fetches_order_book_depth():
    session = FakeSession([
        FakeResponse({
            "lastUpdateId": 123,
            "bids": [
                ["1.00", "10"],
                ["0.99", "20"],
            ],
            "asks": [
                ["1.01", "5"],
                ["1.02", "15"],
            ],
        }),
    ])

    client = WeexPublicSpotClient(
        session=session,
    )

    result = client.fetch_depth(
        symbol="COTIUSDT",
        limit=200,
    )

    assert result[
        "fetch_complete"
    ] is True

    assert result[
        "symbol"
    ] == "COTIUSDT"

    assert result[
        "bids"
    ][0] == [
        "1.00",
        "10",
    ]

    assert result[
        "asks"
    ][0] == [
        "1.01",
        "5",
    ]

    assert session.calls[0][
        "params"
    ] == {
        "symbol": "COTIUSDT",
        "limit": 200,
    }


def test_depth_limit_must_be_supported():
    client = WeexPublicSpotClient(
        session=FakeSession([])
    )

    with pytest.raises(
        ValueError,
        match="limit must be 15 or 200",
    ):
        client.fetch_depth(
            symbol="BTCUSDT",
            limit=100,
        )


def test_depth_symbol_is_required():
    client = WeexPublicSpotClient(
        session=FakeSession([])
    )

    with pytest.raises(
        ValueError,
        match="symbol is required",
    ):
        client.fetch_depth(
            symbol="",
        )


def test_fetches_coin_network_information():
    session = FakeSession([
        FakeResponse([
            {
                "coin": "COTI",
                "name": "COTI",
                "depositAllEnable": True,
                "withdrawAllEnable": True,
                "networkList": [
                    {
                        "network": "ERC20",
                        "isDefault": True,
                        "depositEnable": True,
                        "withdrawEnable": True,
                        "withdrawFee": "10",
                        "withdrawMin": "20",
                        "withdrawIntegerMultiple": "1",
                        "minConfirm": 12,
                    },
                ],
            },
        ]),
    ])

    client = WeexPublicSpotClient(
        session=session,
    )

    result = client.fetch_coins()

    assert result[
        "fetch_complete"
    ] is True

    assert result[
        "coins"
    ][0][
        "coin"
    ] == "COTI"

    network = result[
        "coins"
    ][0][
        "networkList"
    ][0]

    assert network[
        "network"
    ] == "ERC20"

    assert network[
        "depositEnable"
    ] is True

    assert network[
        "withdrawEnable"
    ] is True


def test_http_failure_returns_failed_result():
    session = FakeSession([
        FakeResponse(
            {},
            status_code=500,
        ),
    ])

    client = WeexPublicSpotClient(
        session=session,
    )

    result = client.fetch_symbols()

    assert result[
        "fetch_complete"
    ] is False

    assert result[
        "paper_only"
    ] is True


def test_timeout_must_be_positive():
    with pytest.raises(
        ValueError,
        match="timeout_seconds must be positive",
    ):
        WeexPublicSpotClient(
            session=FakeSession([]),
            timeout_seconds=0,
        )


def test_client_is_paper_safe():
    session = FakeSession([
        FakeResponse([
            "BTCUSDT",
        ]),
    ])

    client = WeexPublicSpotClient(
        session=session,
    )

    result = client.fetch_symbols()

    assert result[
        "paper_only"
    ] is True

    assert result[
        "live_order_submitted"
    ] is False
