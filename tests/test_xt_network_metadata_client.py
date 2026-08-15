import pytest

from exchanges.xt_network_metadata_client import (
    XTNetworkMetadataClient,
)


class FakeResponse:
    def __init__(
        self,
        payload,
        status_code=200,
    ):
        self._payload = payload
        self.status_code = status_code

    def json(self):
        return self._payload

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(
                f"HTTP {self.status_code}"
            )


class FakeSession:
    def __init__(
        self,
        response=None,
        error=None,
    ):
        self._response = response
        self._error = error
        self.calls = []

    def get(
        self,
        url,
        timeout=None,
    ):
        self.calls.append({
            "url": url,
            "timeout": timeout,
        })

        if self._error is not None:
            raise self._error

        return self._response


def _payload():
    return {
        "rc": 0,
        "mc": "SUCCESS",
        "ma": [],
        "result": [
            {
                "currency": "usdt",
                "supportChains": [
                    {
                        "chain": "Tron",
                        "depositEnabled": True,
                        "withdrawEnabled": True,
                        "contract": (
                            "TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t"
                        ),
                        "depositMinAmount": 0.1,
                        "depositFeeRate": 0,
                        "depositConfirmations": 3,
                        "withdrawMinAmount": 10,
                        "withdrawPrecision": 6,
                        "withdrawFeeAmount": 1,
                        "withdrawFeeCurrency": "usdt",
                        "withdrawFeeCurrencyId": 11,
                    },
                    {
                        "chain": "Ethereum",
                        "depositEnabled": True,
                        "withdrawEnabled": False,
                        "contract": (
                            "0xdac17f958d2ee523a2206206994597c13d831ec7"
                        ),
                        "depositMinAmount": 0,
                        "depositFeeRate": 0,
                        "depositConfirmations": 12,
                        "withdrawMinAmount": 10,
                        "withdrawPrecision": 6,
                        "withdrawFeeAmount": 2,
                        "withdrawFeeCurrency": "usdt",
                        "withdrawFeeCurrencyId": 11,
                    },
                ],
            },
        ],
    }


def test_fetches_xt_public_network_metadata():
    session = FakeSession(
        FakeResponse(_payload())
    )

    client = XTNetworkMetadataClient(
        session=session
    )

    result = client.fetch()

    assert result["fetch_complete"] is True
    assert result["exchange_id"] == "xt"
    assert len(result["currencies"]) == 1

    assert session.calls == [
        {
            "url": (
                "https://sapi.xt.com"
                "/v4/public/wallet/support/currency"
            ),
            "timeout": 10,
        },
    ]


def test_preserves_xt_chain_metadata():
    client = XTNetworkMetadataClient(
        session=FakeSession(
            FakeResponse(_payload())
        )
    )

    result = client.fetch()

    chains = (
        result["currencies"][0]
        ["supportChains"]
    )

    assert chains[0]["chain"] == "Tron"
    assert chains[0]["depositEnabled"] is True
    assert chains[0]["withdrawEnabled"] is True
    assert chains[0]["withdrawFeeAmount"] == 1
    assert chains[0]["depositConfirmations"] == 3


def test_non_success_xt_response_fails_closed():
    payload = {
        "rc": 1,
        "mc": "FAILED",
        "result": None,
    }

    client = XTNetworkMetadataClient(
        session=FakeSession(
            FakeResponse(payload)
        )
    )

    result = client.fetch()

    assert result["fetch_complete"] is False
    assert result["currencies"] == []


def test_invalid_result_fails_closed():
    payload = {
        "rc": 0,
        "mc": "SUCCESS",
        "result": None,
    }

    client = XTNetworkMetadataClient(
        session=FakeSession(
            FakeResponse(payload)
        )
    )

    result = client.fetch()

    assert result["fetch_complete"] is False
    assert result["currencies"] == []


def test_transport_failure_fails_closed():
    client = XTNetworkMetadataClient(
        session=FakeSession(
            error=RuntimeError(
                "network unavailable"
            )
        )
    )

    result = client.fetch()

    assert result["fetch_complete"] is False
    assert result["currencies"] == []


def test_requires_session_or_default_session():
    client = XTNetworkMetadataClient()

    assert client is not None


def test_public_metadata_is_paper_safe():
    client = XTNetworkMetadataClient(
        session=FakeSession(
            FakeResponse(_payload())
        )
    )

    result = client.fetch()

    assert result["paper_only"] is True
    assert result["live_order_submitted"] is False
