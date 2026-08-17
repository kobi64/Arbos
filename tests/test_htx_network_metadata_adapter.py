import pytest

from exchanges.htx_network_metadata_adapter import (
    HTXNetworkMetadataAdapter,
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
    adapter = HTXNetworkMetadataAdapter(
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
    adapter = HTXNetworkMetadataAdapter(
        client=FakeClient(),
    )

    assert adapter.get_networks(
        "USDT"
    ) == []


def test_coin_is_normalized():
    adapter = HTXNetworkMetadataAdapter(
        client=FakeClient(),
    )

    result = adapter.describe_networks(
        " usdt "
    )

    assert result["coin"] == "USDT"


def test_coin_is_required():
    adapter = HTXNetworkMetadataAdapter(
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
        HTXNetworkMetadataAdapter(
            client=None,
        )


class SuccessfulClient:
    def fetch_currencies(self):
        return {
            "fetch_complete": True,
            "reason": None,
            "currencies": [
                {
                    "asset": "USDT",
                    "coin": "USDT",
                    "network": "TRX",
                    "chain": "TRX",
                    "deposit": True,
                    "withdraw": True,
                    "withdrawFee": "1.0",
                    "withdrawMin": "10.0",
                },
                {
                    "asset": "USDT",
                    "coin": "USDT",
                    "network": "ETH",
                    "chain": "ETH",
                    "deposit": True,
                    "withdraw": False,
                    "withdrawFee": "5.0",
                    "withdrawMin": "20.0",
                },
            ],
            "read_only": True,
            "paper_only": True,
            "live_order_submitted": False,
            "live_transfer_submitted": False,
        }


def test_htx_networks_use_network_info_contract():
    from exchanges.network_registry import NetworkInfo

    adapter = HTXNetworkMetadataAdapter(
        client=SuccessfulClient(),
    )

    networks = adapter.get_networks(
        "USDT"
    )

    assert len(networks) == 2

    assert all(
        isinstance(network, NetworkInfo)
        for network in networks
    )

    trx = networks[0]

    assert trx.coin == "USDT"
    assert trx.network == "TRX"
    assert trx.deposit_enabled is True
    assert trx.withdraw_enabled is True
    assert trx.withdraw_fee == 1.0
    assert trx.min_withdraw == 10.0


def test_htx_network_info_preserves_disabled_withdrawal():
    adapter = HTXNetworkMetadataAdapter(
        client=SuccessfulClient(),
    )

    networks = adapter.get_networks(
        "USDT"
    )

    eth = networks[1]

    assert eth.network == "ETH"
    assert eth.deposit_enabled is True
    assert eth.withdraw_enabled is False
    assert eth.withdraw_fee == 5.0
    assert eth.min_withdraw == 20.0
