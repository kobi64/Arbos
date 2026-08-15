import pytest

from exchanges.bitget_network_metadata_client import (
    BitgetNetworkMetadataClient,
)


def test_client_has_public_base_url():
    client = BitgetNetworkMetadataClient()

    assert client.base_url == (
        "https://api.bitget.com"
    )


def test_timeout_must_be_positive():
    with pytest.raises(
        ValueError,
        match="timeout_seconds must be positive",
    ):
        BitgetNetworkMetadataClient(
            timeout_seconds=0,
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


def test_fetches_public_coin_metadata():
    session = FakeSession([
        FakeResponse({
            "code": "00000",
            "msg": "success",
            "data": [
                {
                    "coin": "USDT",
                    "transfer": "true",
                    "chains": [
                        {
                            "chain": "ERC20",
                            "withdrawable": "true",
                            "rechargeable": "true",
                            "withdrawFee": "0.8",
                            "depositConfirm": "12",
                            "withdrawConfirm": "96",
                            "minDepositAmount": "0.5",
                            "minWithdrawAmount": "10",
                            "contractAddress": (
                                "0xdac17f958d2ee523a220620699"
                                "4597c13d831ec7"
                            ),
                            "congestion": "normal",
                        },
                        {
                            "chain": "TRC20",
                            "withdrawable": "true",
                            "rechargeable": "true",
                            "withdrawFee": "1.5",
                            "depositConfirm": "3",
                            "withdrawConfirm": "3",
                            "minDepositAmount": "0.01",
                            "minWithdrawAmount": "10",
                            "contractAddress": (
                                "TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t"
                            ),
                            "congestion": "normal",
                        },
                    ],
                },
            ],
        }),
    ])

    client = BitgetNetworkMetadataClient(
        session=session,
    )

    result = client.fetch_currencies()

    assert result[
        "fetch_complete"
    ] is True

    assert len(
        result["currencies"]
    ) == 1

    assert result[
        "currencies"
    ][0][
        "coin"
    ] == "USDT"

    assert len(
        result[
            "currencies"
        ][0][
            "chains"
        ]
    ) == 2

    assert session.calls[0][
        "url"
    ] == (
        "https://api.bitget.com"
        "/api/v2/spot/public/coins"
    )

    assert result[
        "read_only"
    ] is True

    assert result[
        "paper_only"
    ] is True

    assert result[
        "live_order_submitted"
    ] is False

    assert result[
        "live_transfer_submitted"
    ] is False


def test_exchange_error_fails_closed():
    session = FakeSession([
        FakeResponse({
            "code": "40000",
            "msg": "error",
            "data": None,
        }),
    ])

    result = BitgetNetworkMetadataClient(
        session=session,
    ).fetch_currencies()

    assert result[
        "fetch_complete"
    ] is False

    assert result[
        "currencies"
    ] == []


def test_http_failure_fails_closed():
    session = FakeSession([
        FakeResponse(
            {},
            status_code=500,
        ),
    ])

    result = BitgetNetworkMetadataClient(
        session=session,
    ).fetch_currencies()

    assert result[
        "fetch_complete"
    ] is False

    assert result[
        "currencies"
    ] == []
