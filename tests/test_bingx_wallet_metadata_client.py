import pytest

from exchanges.bingx_wallet_metadata_client import (
    BingXWalletMetadataClient,
)


def test_missing_credentials_fail_closed():
    client = BingXWalletMetadataClient(
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
    client = BingXWalletMetadataClient(
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
    client = BingXWalletMetadataClient(
        api_key=None,
        api_secret=None,
    )

    assert client.read_only is True


def test_base_url_defaults_to_bingx_api():
    client = BingXWalletMetadataClient(
        api_key=None,
        api_secret=None,
    )

    assert client.base_url == (
        "https://open-api.bingx.com"
    )


def test_timeout_must_be_positive():
    with pytest.raises(
        ValueError,
        match="timeout_seconds must be positive",
    ):
        BingXWalletMetadataClient(
            api_key=None,
            api_secret=None,
            timeout_seconds=0,
        )
