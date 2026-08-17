import pytest

from exchanges.kucoin_wallet_metadata_client import (
    KuCoinWalletMetadataClient,
)


def test_missing_credentials_fail_closed():
    client = KuCoinWalletMetadataClient(
        api_key=None,
        api_secret=None,
        api_passphrase=None,
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
    client = KuCoinWalletMetadataClient(
        api_key="key",
        api_secret="secret",
        api_passphrase=None,
    )

    result = client.fetch_currencies()

    assert result[
        "fetch_complete"
    ] is False

    assert result[
        "reason"
    ] == "credentials_unavailable"


def test_client_is_read_only():
    client = KuCoinWalletMetadataClient(
        api_key=None,
        api_secret=None,
        api_passphrase=None,
    )

    assert client.read_only is True


def test_base_url_defaults_to_kucoin():
    client = KuCoinWalletMetadataClient(
        api_key=None,
        api_secret=None,
        api_passphrase=None,
    )

    assert client.base_url == (
        "https://api.kucoin.com"
    )


def test_timeout_must_be_positive():
    with pytest.raises(
        ValueError,
        match="timeout_seconds must be positive",
    ):
        KuCoinWalletMetadataClient(
            api_key=None,
            api_secret=None,
            api_passphrase=None,
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


def test_public_currency_detail_is_available_without_credentials():
    session = FakeSession({
        "code": "200000",
        "data": {
            "currency": "USDT",
            "chains": [
                {
                    "chainName": "ERC20",
                    "chainId": "eth",
                    "isDepositEnabled": True,
                    "isWithdrawEnabled": True,
                },
                {
                    "chainName": "TRC20",
                    "chainId": "trx",
                    "isDepositEnabled": True,
                    "isWithdrawEnabled": False,
                },
            ],
        },
    })

    client = KuCoinWalletMetadataClient(
        api_key=None,
        api_secret=None,
        api_passphrase=None,
        session=session,
    )

    result = client.fetch_currency_chains(
        " usdt "
    )

    assert result[
        "fetch_complete"
    ] is True

    assert result[
        "currency"
    ] == "USDT"

    assert len(
        result["currencies"]
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
    ][1]["network"] == "TRX"

    assert result[
        "currencies"
    ][1]["withdraw"] is False

    assert (
        session.calls[0]["url"]
        .endswith(
            "/api/v3/currencies/USDT"
        )
    )


def test_public_currency_detail_transport_failure_fails_closed():
    class BrokenSession:
        def get(
            self,
            *args,
            **kwargs,
        ):
            raise RuntimeError(
                "offline"
            )

    client = KuCoinWalletMetadataClient(
        api_key=None,
        api_secret=None,
        api_passphrase=None,
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


def test_public_currency_detail_api_failure_fails_closed():
    session = FakeSession({
        "code": "400100",
        "msg": "bad request",
    })

    client = KuCoinWalletMetadataClient(
        api_key=None,
        api_secret=None,
        api_passphrase=None,
        session=session,
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
        "400100"
        in result["reason"]
    )
