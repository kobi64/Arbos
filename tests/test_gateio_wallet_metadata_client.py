import pytest

from exchanges.gateio_wallet_metadata_client import (
    GateIOWalletMetadataClient,
)


def test_missing_credentials_fail_closed():
    client = GateIOWalletMetadataClient(
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
    client = GateIOWalletMetadataClient(
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
    client = GateIOWalletMetadataClient(
        api_key=None,
        api_secret=None,
    )

    assert client.read_only is True


def test_base_url_defaults_to_gateio():
    client = GateIOWalletMetadataClient(
        api_key=None,
        api_secret=None,
    )

    assert client.base_url == (
        "https://api.gateio.ws"
    )


def test_timeout_must_be_positive():
    with pytest.raises(
        ValueError,
        match="timeout_seconds must be positive",
    ):
        GateIOWalletMetadataClient(
            api_key=None,
            api_secret=None,
            timeout_seconds=0,
        )


class FakeResponse:
    def __init__(
        self,
        payload,
    ):
        self._payload = payload

    def raise_for_status(
        self,
    ):
        return None

    def json(
        self,
    ):
        return self._payload


class FakeSession:
    def __init__(
        self,
        payload,
    ):
        self.payload = payload
        self.calls = []

    def get(
        self,
        url,
        params=None,
        timeout=None,
        headers=None,
    ):
        self.calls.append({
            "url": url,
            "params": params,
            "timeout": timeout,
            "headers": headers,
        })

        return FakeResponse(
            self.payload
        )


def test_public_currency_chains_are_available_without_credentials():
    session = FakeSession([
        {
            "chain": "ETH",
            "name_en": "ETH/ERC20",
            "is_deposit_disabled": 0,
            "is_withdraw_disabled": 0,
        },
        {
            "chain": "TRX",
            "name_en": "TRON/TRC20",
            "is_deposit_disabled": 0,
            "is_withdraw_disabled": 1,
        },
    ])

    client = GateIOWalletMetadataClient(
        api_key=None,
        api_secret=None,
        session=session,
    )

    result = client.fetch_currency_chains(
        "USDT"
    )

    assert result[
        "fetch_complete"
    ] is True

    assert result[
        "currency"
    ] == "USDT"

    assert len(
        result[
            "currencies"
        ]
    ) == 2

    assert result[
        "currencies"
    ][0]["asset"] == "USDT"

    assert result[
        "currencies"
    ][0]["network"] == "ETH"

    assert result[
        "currencies"
    ][0]["deposit"] is True

    assert result[
        "currencies"
    ][0]["withdraw"] is True

    assert result[
        "currencies"
    ][1]["withdraw"] is False

    assert session.calls[0][
        "params"
    ] == {
        "currency": "USDT",
    }


def test_public_currency_chain_transport_failure_fails_closed():
    class BrokenSession:
        def get(
            self,
            *args,
            **kwargs,
        ):
            raise RuntimeError(
                "offline"
            )

    client = GateIOWalletMetadataClient(
        api_key=None,
        api_secret=None,
        session=BrokenSession(),
    )

    result = client.fetch_currency_chains(
        "USDT"
    )

    assert result[
        "fetch_complete"
    ] is False

    assert result[
        "currencies"
    ] == []

    assert (
        "RuntimeError"
        in result["reason"]
    )


def test_authenticated_currency_metadata_requires_credentials():
    client = GateIOWalletMetadataClient(
        api_key=None,
        api_secret=None,
    )

    result = client.fetch_currencies()

    assert result["fetch_complete"] is False
    assert result["reason"] == "credentials_unavailable"
    assert result["currencies"] == []
    assert result["read_only"] is True
    assert result["live_order_submitted"] is False
    assert result["live_transfer_submitted"] is False


def test_authenticated_currency_metadata_accepts_injected_time_provider():
    client = GateIOWalletMetadataClient(
        api_key="test-key",
        api_secret="test-secret",
        time_provider=lambda: 1700000000,
    )

    assert client._time_provider() == 1700000000


def test_authenticated_currency_metadata_transport_failure_fails_closed():
    class BrokenSession:
        def get(
            self,
            *args,
            **kwargs,
        ):
            raise RuntimeError(
                "offline"
            )

    client = GateIOWalletMetadataClient(
        api_key="test-key",
        api_secret="test-secret",
        session=BrokenSession(),
        time_provider=lambda: 1700000000,
    )

    result = client.fetch_currencies()

    assert result["fetch_complete"] is False
    assert result["currencies"] == []
    assert result["read_only"] is True
    assert result["live_order_submitted"] is False
    assert result["live_transfer_submitted"] is False


def test_authenticated_withdraw_status_uses_gate_v4_signature():
    import hashlib
    import hmac

    session = FakeSession([
        {
            "currency": "USDT",
            "withdraw_fix": "2.5",
            "withdraw_fix_on_chains": {
                "ETH": "3.5",
                "TRX": "1",
            },
        },
    ])

    timestamp = 1700000000

    client = GateIOWalletMetadataClient(
        api_key="test-key",
        api_secret="test-secret",
        session=session,
        time_provider=lambda: timestamp,
    )

    result = client.fetch_currencies()

    assert result["fetch_complete"] is True
    assert result["currencies"][0][
        "currency"
    ] == "USDT"

    call = session.calls[0]

    path = (
        "/api/v4/wallet/"
        "withdraw_status"
    )

    assert call["url"] == (
        "https://api.gateio.ws"
        f"{path}"
    )

    assert call["params"] is None

    body_hash = hashlib.sha512(
        b""
    ).hexdigest()

    signing_string = "\n".join([
        "GET",
        path,
        "",
        body_hash,
        str(timestamp),
    ])

    expected_signature = hmac.new(
        b"test-secret",
        signing_string.encode(
            "utf-8"
        ),
        hashlib.sha512,
    ).hexdigest()

    assert call["headers"] == {
        "KEY": "test-key",
        "Timestamp": str(
            timestamp
        ),
        "SIGN": expected_signature,
    }


def test_authenticated_withdraw_status_rejects_invalid_payload():
    session = FakeSession({
        "unexpected": "payload",
    })

    client = GateIOWalletMetadataClient(
        api_key="test-key",
        api_secret="test-secret",
        session=session,
        time_provider=lambda: 1700000000,
    )

    result = client.fetch_currencies()

    assert result[
        "fetch_complete"
    ] is False

    assert result[
        "currencies"
    ] == []

    assert (
        "ValueError"
        in result["reason"]
    )


def test_authenticated_withdraw_status_uses_gate_v4_signature():
    import hashlib
    import hmac

    session = FakeSession([
        {
            "currency": "USDT",
            "withdraw_fix": "2.5",
            "withdraw_fix_on_chains": {
                "ETH": "3.5",
                "TRX": "1",
            },
        },
    ])

    timestamp = 1700000000

    client = GateIOWalletMetadataClient(
        api_key="test-key",
        api_secret="test-secret",
        session=session,
        time_provider=lambda: timestamp,
    )

    result = client.fetch_currencies()

    assert result["fetch_complete"] is True
    assert result["currencies"][0][
        "currency"
    ] == "USDT"

    call = session.calls[0]

    path = (
        "/api/v4/wallet/"
        "withdraw_status"
    )

    assert call["url"] == (
        "https://api.gateio.ws"
        f"{path}"
    )

    assert call["params"] is None

    body_hash = hashlib.sha512(
        b""
    ).hexdigest()

    signing_string = "\n".join([
        "GET",
        path,
        "",
        body_hash,
        str(timestamp),
    ])

    expected_signature = hmac.new(
        b"test-secret",
        signing_string.encode(
            "utf-8"
        ),
        hashlib.sha512,
    ).hexdigest()

    assert call["headers"] == {
        "KEY": "test-key",
        "Timestamp": str(
            timestamp
        ),
        "SIGN": expected_signature,
    }


def test_authenticated_withdraw_status_rejects_invalid_payload():
    session = FakeSession({
        "unexpected": "payload",
    })

    client = GateIOWalletMetadataClient(
        api_key="test-key",
        api_secret="test-secret",
        session=session,
        time_provider=lambda: 1700000000,
    )

    result = client.fetch_currencies()

    assert result[
        "fetch_complete"
    ] is False

    assert result[
        "currencies"
    ] == []

    assert (
        "ValueError"
        in result["reason"]
    )


def test_authenticated_withdraw_status_uses_gate_v4_signature():
    import hashlib
    import hmac

    session = FakeSession([
        {
            "currency": "USDT",
            "withdraw_fix": "2.5",
            "withdraw_fix_on_chains": {
                "ETH": "3.5",
                "TRX": "1",
            },
        },
    ])

    timestamp = 1700000000

    client = GateIOWalletMetadataClient(
        api_key="test-key",
        api_secret="test-secret",
        session=session,
        time_provider=lambda: timestamp,
    )

    result = client.fetch_currencies()

    assert result["fetch_complete"] is True
    assert result["currencies"][0][
        "currency"
    ] == "USDT"

    call = session.calls[0]

    path = (
        "/api/v4/wallet/"
        "withdraw_status"
    )

    assert call["url"] == (
        "https://api.gateio.ws"
        f"{path}"
    )

    assert call["params"] is None

    body_hash = hashlib.sha512(
        b""
    ).hexdigest()

    signing_string = "\n".join([
        "GET",
        path,
        "",
        body_hash,
        str(timestamp),
    ])

    expected_signature = hmac.new(
        b"test-secret",
        signing_string.encode(
            "utf-8"
        ),
        hashlib.sha512,
    ).hexdigest()

    assert call["headers"] == {
        "KEY": "test-key",
        "Timestamp": str(
            timestamp
        ),
        "SIGN": expected_signature,
    }


def test_authenticated_withdraw_status_rejects_invalid_payload():
    session = FakeSession({
        "unexpected": "payload",
    })

    client = GateIOWalletMetadataClient(
        api_key="test-key",
        api_secret="test-secret",
        session=session,
        time_provider=lambda: 1700000000,
    )

    result = client.fetch_currencies()

    assert result[
        "fetch_complete"
    ] is False

    assert result[
        "currencies"
    ] == []

    assert (
        "ValueError"
        in result["reason"]
    )
