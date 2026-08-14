import pytest

from exchanges.mexc_wallet_metadata_client import (
    MexcWalletMetadataClient,
)


def test_missing_credentials_fail_closed():
    client = MexcWalletMetadataClient(
        api_key=None,
        api_secret=None,
    )

    result = client.fetch_currencies()

    assert result[
        "fetch_complete"
    ] is False

    assert result[
        "reason"
    ] == "credentials_unavailable"

    assert result[
        "currencies"
    ] == []

    assert result[
        "paper_only"
    ] is True

    assert result[
        "live_order_submitted"
    ] is False

    assert result[
        "live_transfer_submitted"
    ] is False


def test_partial_credentials_fail_closed():
    client = MexcWalletMetadataClient(
        api_key="key",
        api_secret=None,
    )

    result = client.fetch_currencies()

    assert result[
        "fetch_complete"
    ] is False

    assert result[
        "reason"
    ] == "credentials_unavailable"


def test_client_is_read_only():
    client = MexcWalletMetadataClient(
        api_key=None,
        api_secret=None,
    )

    assert client.read_only is True


def test_base_url_defaults_to_mexc_api():
    client = MexcWalletMetadataClient(
        api_key=None,
        api_secret=None,
    )

    assert client.base_url == (
        "https://api.mexc.com"
    )


def test_timeout_must_be_positive():
    with pytest.raises(
        ValueError,
        match="timeout_seconds must be positive",
    ):
        MexcWalletMetadataClient(
            api_key=None,
            api_secret=None,
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
        self.responses = list(
            responses
        )
        self.calls = []

    def get(
        self,
        url,
        params=None,
        headers=None,
        timeout=None,
    ):
        self.calls.append({
            "url": url,
            "params": params,
            "headers": headers,
            "timeout": timeout,
        })

        return self.responses.pop(0)


def test_signed_currency_metadata_request():
    session = FakeSession([
        FakeResponse([
            {
                "coin": "USDT",
                "networkList": [
                    {
                        "coin": "USDT",
                        "network": "TRX",
                        "depositEnable": True,
                        "withdrawEnable": True,
                        "withdrawFee": "1",
                        "withdrawMin": "10",
                        "minConfirm": 20,
                        "contract": "TR7TEST",
                    },
                ],
            },
        ]),
    ])

    client = MexcWalletMetadataClient(
        api_key="test-key",
        api_secret="test-secret",
        session=session,
        time_provider=lambda: 1700000000.0,
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

    call = session.calls[0]

    assert call[
        "url"
    ] == (
        "https://api.mexc.com"
        "/api/v3/capital/config/getall"
    )

    assert call[
        "headers"
    ][
        "X-MEXC-APIKEY"
    ] == "test-key"

    assert call[
        "params"
    ][
        "timestamp"
    ] == 1700000000000

    assert "signature" in call[
        "params"
    ]


def test_signature_is_hmac_sha256():
    import hashlib
    import hmac

    client = MexcWalletMetadataClient(
        api_key="test-key",
        api_secret="test-secret",
        time_provider=lambda: 1700000000.0,
    )

    expected = hmac.new(
        b"test-secret",
        b"timestamp=1700000000000",
        hashlib.sha256,
    ).hexdigest()

    assert client._sign(
        "timestamp=1700000000000"
    ) == expected


def test_authenticated_http_failure_is_fail_closed():
    session = FakeSession([
        FakeResponse(
            {},
            status_code=500,
        ),
    ])

    client = MexcWalletMetadataClient(
        api_key="test-key",
        api_secret="test-secret",
        session=session,
        time_provider=lambda: 1700000000.0,
    )

    result = client.fetch_currencies()

    assert result[
        "fetch_complete"
    ] is False

    assert result[
        "currencies"
    ] == []

    assert result[
        "paper_only"
    ] is True

    assert result[
        "live_order_submitted"
    ] is False

    assert result[
        "live_transfer_submitted"
    ] is False


def test_authenticated_payload_must_be_list():
    session = FakeSession([
        FakeResponse({
            "unexpected": True,
        }),
    ])

    client = MexcWalletMetadataClient(
        api_key="test-key",
        api_secret="test-secret",
        session=session,
        time_provider=lambda: 1700000000.0,
    )

    result = client.fetch_currencies()

    assert result[
        "fetch_complete"
    ] is False
