import pytest

from exchanges.phemex_network_metadata_client import (
    PhemexNetworkMetadataClient,
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
        self._response = response
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

        return self._response


def valid_payload():
    return {
        "code": 0,
        "msg": "OK",
        "data": {
            "USDT": [
                {
                    "currencyCode": 3,
                    "currencyName": "USDT",
                    "chainName": "TRX",
                    "chainId": 11,
                    "displayName": "TRC20",
                    "displayNetwork": "TRX",
                    "inUse": True,
                    "permanentlyClosed": 0,
                },
                {
                    "currencyCode": 3,
                    "currencyName": "USDT",
                    "chainName": "ETH",
                    "chainId": 4,
                    "displayName": "ERC20",
                    "displayNetwork": "ETH",
                    "inUse": True,
                    "permanentlyClosed": 0,
                },
            ]
        },
    }


def test_fetch_networks_calls_public_endpoint():
    session = FakeSession(
        FakeResponse(
            valid_payload()
        )
    )

    client = PhemexNetworkMetadataClient(
        session=session,
    )

    result = client.fetch_networks(
        "usdt"
    )

    assert result["code"] == 0

    assert session.calls == [
        {
            "url": (
                "https://api.phemex.com"
                "/exchange/public/cfg/"
                "chain-settings"
            ),
            "params": {
                "currency": "USDT",
            },
            "timeout": 10.0,
        }
    ]


def test_currency_is_normalized():
    session = FakeSession(
        FakeResponse(
            valid_payload()
        )
    )

    client = PhemexNetworkMetadataClient(
        session=session,
    )

    client.fetch_networks(
        " usdt "
    )

    assert session.calls[0][
        "params"
    ]["currency"] == "USDT"


def test_currency_is_required():
    client = PhemexNetworkMetadataClient(
        session=FakeSession(
            FakeResponse(
                valid_payload()
            )
        )
    )

    with pytest.raises(
        ValueError,
        match="currency is required",
    ):
        client.fetch_networks("")


def test_timeout_must_be_positive():
    with pytest.raises(
        ValueError,
        match="timeout_seconds must be positive",
    ):
        PhemexNetworkMetadataClient(
            timeout_seconds=0,
        )


def test_http_failure_is_wrapped():
    client = PhemexNetworkMetadataClient(
        session=FakeSession(
            FakeResponse(
                {},
                status_code=500,
            )
        )
    )

    with pytest.raises(
        RuntimeError,
        match="Phemex network metadata unavailable",
    ):
        client.fetch_networks(
            "USDT"
        )


def test_non_dict_payload_is_rejected():
    client = PhemexNetworkMetadataClient(
        session=FakeSession(
            FakeResponse(
                [],
            )
        )
    )

    with pytest.raises(
        RuntimeError,
        match="Phemex network metadata unavailable",
    ):
        client.fetch_networks(
            "USDT"
        )


def test_client_is_read_only():
    client = PhemexNetworkMetadataClient(
        session=FakeSession(
            FakeResponse(
                valid_payload()
            )
        )
    )

    assert client.read_only is True
