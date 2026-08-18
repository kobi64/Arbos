import pytest

from exchanges.weex_network_metadata_adapter import (
    WeexNetworkMetadataAdapter,
)


class FakeProvider:
    def get_coin(
        self,
        coin,
    ):
        if coin == "UNKNOWN":
            return {
                "exchange": "weex",
                "coin": coin,
                "available": False,
                "reason": "coin_not_found",
                "paper_only": True,
                "live_order_submitted": False,
            }

        return {
            "exchange": "weex",
            "coin": coin,
            "available": True,
            "network_metadata_available": True,
            "network_metadata_reason": None,
            "transfer_verification_available": True,
            "deposit_enabled": True,
            "withdraw_enabled": True,
            "networks": [
                {
                    "network": "TRC20",
                    "raw_network": "Tron (TRC20)",
                    "deposit_enabled": True,
                    "withdraw_enabled": True,
                    "withdraw_fee": 1.5,
                    "withdraw_min": 10.0,
                    "min_confirmations": 20,
                },
                {
                    "network": "ERC20",
                    "raw_network": "Ethereum (ETH)",
                    "deposit_enabled": True,
                    "withdraw_enabled": False,
                    "withdraw_fee": 1.0,
                    "withdraw_min": 20.0,
                    "min_confirmations": 12,
                },
            ],
            "paper_only": True,
            "live_order_submitted": False,
        }


def test_converts_weex_networks_to_network_info():
    adapter = WeexNetworkMetadataAdapter(
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
    assert trc20.withdraw_fee == 1.5
    assert trc20.min_withdraw == 10.0


def test_preserves_disabled_withdrawal():
    adapter = WeexNetworkMetadataAdapter(
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
    assert erc20.withdraw_fee == 1.0
    assert erc20.min_withdraw == 20.0


def test_unknown_coin_returns_empty_list():
    adapter = WeexNetworkMetadataAdapter(
        provider=FakeProvider(),
    )

    assert adapter.get_networks(
        "UNKNOWN"
    ) == []


def test_coin_is_normalized():
    class RecordingProvider:
        def __init__(self):
            self.coin = None

        def get_coin(
            self,
            coin,
        ):
            self.coin = coin

            return {
                "available": False,
                "reason": "coin_not_found",
            }

    provider = RecordingProvider()

    adapter = WeexNetworkMetadataAdapter(
        provider=provider,
    )

    adapter.get_networks(
        " usdt "
    )

    assert provider.coin == "USDT"


def test_coin_is_required():
    adapter = WeexNetworkMetadataAdapter(
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
        WeexNetworkMetadataAdapter(
            provider=None,
        )


def test_empty_network_metadata_is_distinguishable():
    class EmptyNetworkProvider:
        def get_coin(
            self,
            coin,
        ):
            return {
                "exchange": "weex",
                "coin": coin,
                "available": True,
                "network_metadata_available": False,
                "network_metadata_reason": (
                    "empty_network_list"
                ),
                "transfer_verification_available": False,
                "networks": [],
                "paper_only": True,
                "live_order_submitted": False,
            }

    adapter = WeexNetworkMetadataAdapter(
        provider=EmptyNetworkProvider(),
    )

    result = adapter.describe_networks(
        "FIR"
    )

    assert result[
        "coin"
    ] == "FIR"

    assert result[
        "network_metadata_available"
    ] is False

    assert result[
        "network_metadata_reason"
    ] == "empty_network_list"

    assert result[
        "transfer_verification_available"
    ] is False

    assert result[
        "networks"
    ] == []


def test_describe_networks_preserves_normal_networks():
    adapter = WeexNetworkMetadataAdapter(
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


def test_unknown_minimum_withdrawal_is_preserved():
    class UnknownMinimumProvider:
        def get_coin(
            self,
            coin,
        ):
            return {
                "exchange": "weex",
                "coin": coin,
                "available": True,
                "networks": [
                    {
                        "network": "TRC20",
                        "deposit_enabled": True,
                        "withdraw_enabled": True,
                        "withdraw_fee": 1.0,
                        "withdraw_min": None,
                    },
                ],
                "paper_only": True,
                "live_order_submitted": False,
            }

    adapter = WeexNetworkMetadataAdapter(
        provider=UnknownMinimumProvider(),
    )

    networks = adapter.get_networks(
        "USDT"
    )

    assert len(networks) == 1
    assert networks[0].min_withdraw is None


def test_network_metadata_does_not_imply_transfer_verification():
    class MetadataOnlyProvider:
        def get_coin(
            self,
            coin,
        ):
            return {
                "exchange": "weex",
                "coin": coin,
                "available": True,
                "network_metadata_available": True,
                "networks": [
                    {
                        "network": "TRC20",
                        "deposit_enabled": True,
                        "withdraw_enabled": True,
                    },
                ],
            }

    result = WeexNetworkMetadataAdapter(
        provider=MetadataOnlyProvider(),
    ).describe_networks(
        "USDT"
    )

    assert result[
        "network_metadata_available"
    ] is True

    assert result[
        "transfer_verification_available"
    ] is False
