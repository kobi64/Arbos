import pytest

from exchanges.lbank_network_metadata_adapter import (
    LBankNetworkMetadataAdapter,
)


class FakeProvider:
    def get_coin(
        self,
        coin,
    ):
        if coin == "UNKNOWN":
            return {
                "exchange": "lbank",
                "coin": coin,
                "available": True,
                "network_metadata_available": False,
                "network_metadata_reason": "empty_network_list",
                "transfer_verification_available": False,
                "networks": [],
            }

        return {
            "exchange": "lbank",
            "coin": coin,
            "available": True,
            "network_metadata_available": True,
            "network_metadata_reason": None,
            "transfer_verification_available": True,
            "networks": [
                {
                    "asset": "USDT",
                    "network": "ETH",
                    "raw_network": "erc20",
                    "deposit_enabled": True,
                    "withdraw_enabled": True,
                    "withdraw_fee": 1.0,
                    "min_withdraw": 10.0,
                    "min_deposit": 0.0001,
                    "contract_address": (
                        "0xdac17f958d2ee523a2206206994597c13d831ec7"
                    ),
                    "memo_required": False,
                },
                {
                    "asset": "USDT",
                    "network": "OMNI",
                    "raw_network": "omni",
                    "deposit_enabled": False,
                    "withdraw_enabled": False,
                    "withdraw_fee": None,
                    "min_withdraw": 0.0,
                    "min_deposit": 0.0,
                    "contract_address": None,
                    "memo_required": False,
                },
            ],
        }


def test_converts_lbank_networks_to_network_info():
    adapter = LBankNetworkMetadataAdapter(
        provider=FakeProvider(),
    )

    networks = adapter.get_networks(
        "USDT"
    )

    assert len(networks) == 2

    eth = next(
        item
        for item in networks
        if item.network == "ETH"
    )

    assert eth.coin == "USDT"
    assert eth.deposit_enabled is True
    assert eth.withdraw_enabled is True
    assert eth.withdraw_fee == 1.0
    assert eth.min_withdraw == 10.0


def test_preserves_disabled_transfer_state():
    adapter = LBankNetworkMetadataAdapter(
        provider=FakeProvider(),
    )

    networks = adapter.get_networks(
        "USDT"
    )

    omni = next(
        item
        for item in networks
        if item.network == "OMNI"
    )

    assert omni.deposit_enabled is False
    assert omni.withdraw_enabled is False


def test_unknown_coin_returns_empty_list():
    adapter = LBankNetworkMetadataAdapter(
        provider=FakeProvider(),
    )

    assert adapter.get_networks(
        "UNKNOWN"
    ) == []


def test_describe_networks_preserves_status():
    adapter = LBankNetworkMetadataAdapter(
        provider=FakeProvider(),
    )

    result = adapter.describe_networks(
        "USDT"
    )

    assert result[
        "network_metadata_available"
    ] is True

    assert result[
        "transfer_verification_available"
    ] is True

    assert len(
        result["networks"]
    ) == 2


def test_coin_is_required():
    adapter = LBankNetworkMetadataAdapter(
        provider=FakeProvider(),
    )

    with pytest.raises(
        ValueError,
        match="coin is required",
    ):
        adapter.get_networks("")


def test_provider_is_required():
    with pytest.raises(
        ValueError,
        match="provider is required",
    ):
        LBankNetworkMetadataAdapter(
            provider=None,
        )
