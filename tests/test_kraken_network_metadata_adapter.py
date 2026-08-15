import pytest

from exchanges.kraken_network_metadata_adapter import (
    KrakenNetworkMetadataAdapter,
)


class FakeClient:
    def fetch_currencies(self):
        return {
            "fetch_complete": False,
            "reason": "credentials_unavailable",
            "currencies": [],
            "read_only": True,
            "paper_only": True,
            "live_order_submitted": False,
            "live_transfer_submitted": False,
        }


def test_credentials_unavailable_fails_closed():
    adapter = KrakenNetworkMetadataAdapter(
        client=FakeClient(),
    )

    result = adapter.describe_networks(
        "USDT"
    )

    assert result[
        "network_metadata_available"
    ] is False

    assert result[
        "network_metadata_reason"
    ] == "credentials_unavailable"

    assert result[
        "transfer_verification_available"
    ] is False

    assert result[
        "networks"
    ] == []


def test_get_networks_returns_empty_list():
    adapter = KrakenNetworkMetadataAdapter(
        client=FakeClient(),
    )

    assert adapter.get_networks(
        "USDT"
    ) == []


def test_coin_is_normalized():
    adapter = KrakenNetworkMetadataAdapter(
        client=FakeClient(),
    )

    result = adapter.describe_networks(
        " usdt "
    )

    assert result["coin"] == "USDT"


def test_coin_is_required():
    adapter = KrakenNetworkMetadataAdapter(
        client=FakeClient(),
    )

    with pytest.raises(
        ValueError,
        match="coin is required",
    ):
        adapter.describe_networks("")


def test_client_is_required():
    with pytest.raises(
        ValueError,
        match="client is required",
    ):
        KrakenNetworkMetadataAdapter(
            client=None,
        )
