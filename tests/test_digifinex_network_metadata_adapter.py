import pytest

from exchanges.digifinex_network_metadata_adapter import (
    DigiFinexNetworkMetadataAdapter,
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
    adapter = DigiFinexNetworkMetadataAdapter(
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
    adapter = DigiFinexNetworkMetadataAdapter(
        client=FakeClient(),
    )

    assert adapter.get_networks(
        "USDT"
    ) == []


def test_coin_is_normalized():
    adapter = DigiFinexNetworkMetadataAdapter(
        client=FakeClient(),
    )

    result = adapter.describe_networks(
        " usdt "
    )

    assert result["coin"] == "USDT"


def test_coin_is_required():
    adapter = DigiFinexNetworkMetadataAdapter(
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
        DigiFinexNetworkMetadataAdapter(
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
                    "network": "TRC20",
                    "deposit_enabled": True,
                    "withdraw_enabled": True,
                    "withdraw_fee": "1.0",
                    "minimum_withdrawal": "10",
                    "confirmations": "3",
                },
                {
                    "asset": "USDT",
                    "network": "ERC20",
                    "deposit_enabled": True,
                    "withdraw_enabled": False,
                    "withdraw_fee": "3.5",
                    "minimum_withdrawal": "10",
                    "confirmations": "12",
                },
            ],
            "read_only": True,
            "paper_only": True,
            "live_order_submitted": False,
            "live_transfer_submitted": False,
        }


def test_digifinex_networks_use_network_info_contract():
    from exchanges.network_registry import NetworkInfo

    adapter = DigiFinexNetworkMetadataAdapter(
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

    trc20 = networks[0]

    assert trc20.coin == "USDT"
    assert trc20.network == "TRC20"
    assert trc20.deposit_enabled is True
    assert trc20.withdraw_enabled is True
    assert trc20.withdraw_fee == 1.0
    assert trc20.min_withdraw == 10.0
    assert trc20.confirmations == 3


def test_digifinex_network_info_preserves_disabled_withdrawal():
    adapter = DigiFinexNetworkMetadataAdapter(
        client=SuccessfulClient(),
    )

    networks = adapter.get_networks(
        "USDT"
    )

    erc20 = networks[1]

    assert erc20.network == "ERC20"
    assert erc20.deposit_enabled is True
    assert erc20.withdraw_enabled is False
    assert erc20.withdraw_fee == 3.5
    assert erc20.min_withdraw == 10.0
    assert erc20.confirmations == 12
