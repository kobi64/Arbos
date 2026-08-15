import pytest

from exchanges.digifinex_wallet_metadata_client import (
    DigiFinexWalletMetadataClient,
)


def test_missing_credentials_fail_closed():
    client = DigiFinexWalletMetadataClient(
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
    client = DigiFinexWalletMetadataClient(
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
    client = DigiFinexWalletMetadataClient(
        api_key=None,
        api_secret=None,
    )

    assert client.read_only is True


def test_base_url_defaults_to_digifinex():
    client = DigiFinexWalletMetadataClient(
        api_key=None,
        api_secret=None,
    )

    assert client.base_url == (
        "https://openapi.digifinex.com"
    )


def test_timeout_must_be_positive():
    with pytest.raises(
        ValueError,
        match="timeout_seconds must be positive",
    ):
        DigiFinexWalletMetadataClient(
            api_key=None,
            api_secret=None,
            timeout_seconds=0,
        )
