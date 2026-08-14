import pytest

from exchanges.poloniex_network_metadata_adapter import (
    PoloniexNetworkMetadataAdapter,
)


class FakeProvider:
    def get_coin(
        self,
        coin,
    ):
        if coin == "UNKNOWN":
            return {
                "exchange": "poloniex",
                "coin": coin,
                "available": False,
                "reason": "coin_not_found",
                "network_metadata_available": False,
                "transfer_verification_available": False,
                "networks": [],
            }

        return {
            "exchange": "poloniex",
            "coin": coin,
            "available": True,
            "network_metadata_available": True,
            "transfer_verification_available": True,
            "networks": [
                {
                    "network": "TRC20",
                    "raw_network": "TRX",
                    "network_name": "Tron",
                    "deposit_enabled": True,
                    "withdraw_enabled": True,
                    "withdraw_fee": 1.0,
                    "min_withdraw": 10.0,
                    "confirmations": 20,
                    "contract_address": (
                        "TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t"
                    ),
                },
                {
                    "network": "ERC20",
                    "raw_network": "ETH",
                    "network_name": "Ethereum",
                    "deposit_enabled": True,
                    "withdraw_enabled": False,
                    "withdraw_fee": 5.0,
                    "min_withdraw": 20.0,
                    "confirmations": 12,
                    "contract_address": (
                        "0xdac17f958d2ee523a2206206994597c13d831ec7"
                    ),
                },
            ],
        }


def test_converts_poloniex_networks_to_network_info():
    adapter = PoloniexNetworkMetadataAdapter(
        provider=FakeProvider(),
    )

    networks = adapter.get_networks(
        "USDT"
    )

    assert len(networks) == 2

    trc20 = next(
        network
        for network in networks
        if network.network == "TRC20"
    )

    assert trc20.coin == "USDT"
    assert trc20.deposit_enabled is True
    assert trc20.withdraw_enabled is True
    assert trc20.withdraw_fee == 1.0
    assert trc20.min_withdraw == 10.0


def test_preserves_disabled_withdrawal():
    adapter = PoloniexNetworkMetadataAdapter(
        provider=FakeProvider(),
    )

    networks = adapter.get_networks(
        "USDT"
    )

    erc20 = next(
        network
        for network in networks
        if network.network == "ERC20"
    )

    assert erc20.deposit_enabled is True
    assert erc20.withdraw_enabled is False


def test_unknown_coin_returns_empty_list():
    adapter = PoloniexNetworkMetadataAdapter(
        provider=FakeProvider(),
    )

    assert adapter.get_networks(
        "UNKNOWN"
    ) == []


def test_describe_networks_preserves_metadata_status():
    adapter = PoloniexNetworkMetadataAdapter(
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
    adapter = PoloniexNetworkMetadataAdapter(
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
        PoloniexNetworkMetadataAdapter(
            provider=None,
        )
