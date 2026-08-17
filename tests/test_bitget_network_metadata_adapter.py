import pytest

from exchanges.bitget_network_metadata_adapter import (
    BitgetNetworkMetadataAdapter,
)


class FakeClient:
    def fetch_currencies(self):
        return {
            "fetch_complete": True,
            "reason": None,
            "currencies": [
                {
                    "coin": "USDT",
                    "transfer": "true",
                    "chains": [
                        {
                            "chain": "ERC20",
                            "withdrawable": "true",
                            "rechargeable": "true",
                            "withdrawFee": "0.8",
                            "depositConfirm": "12",
                            "withdrawConfirm": "96",
                            "minDepositAmount": "0.5",
                            "minWithdrawAmount": "10",
                            "contractAddress": (
                                "0xdac17f958d2ee523a220620699"
                                "4597c13d831ec7"
                            ),
                            "congestion": "normal",
                        },
                        {
                            "chain": "TRC20",
                            "withdrawable": "true",
                            "rechargeable": "true",
                            "withdrawFee": "1.5",
                            "depositConfirm": "3",
                            "withdrawConfirm": "3",
                            "minDepositAmount": "0.01",
                            "minWithdrawAmount": "10",
                            "contractAddress": (
                                "TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t"
                            ),
                            "congestion": "normal",
                        },
                    ],
                },
            ],
            "read_only": True,
            "paper_only": True,
            "live_order_submitted": False,
            "live_transfer_submitted": False,
        }


class FailedClient:
    def fetch_currencies(self):
        return {
            "fetch_complete": False,
            "reason": "exchange_error",
            "currencies": [],
            "read_only": True,
            "paper_only": True,
            "live_order_submitted": False,
            "live_transfer_submitted": False,
        }


def test_client_is_required():
    with pytest.raises(
        ValueError,
        match="client is required",
    ):
        BitgetNetworkMetadataAdapter(
            client=None,
        )


def test_describes_bitget_networks():
    adapter = BitgetNetworkMetadataAdapter(
        client=FakeClient(),
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

    erc20 = result[
        "networks"
    ][0]

    assert erc20.coin == "USDT"
    assert erc20.network == "ETH"
    assert erc20.withdraw_enabled is True
    assert erc20.deposit_enabled is True
    assert erc20.withdraw_fee == 0.8
    assert erc20.min_withdraw == 10.0
    assert erc20.confirmations == 12


def test_networks_use_network_info_contract():
    adapter = BitgetNetworkMetadataAdapter(
        client=FakeClient(),
    )

    networks = adapter.describe_networks(
        "USDT"
    )["networks"]

    assert len(networks) == 2

    ethereum = networks[0]
    tron = networks[1]

    assert ethereum.coin == "USDT"
    assert ethereum.network == "ETH"
    assert ethereum.deposit_enabled is True
    assert ethereum.withdraw_enabled is True
    assert ethereum.withdraw_fee == 0.8
    assert ethereum.min_withdraw == 10.0
    assert ethereum.confirmations == 12

    assert tron.coin == "USDT"
    assert tron.network == "TRON"
    assert tron.deposit_enabled is True
    assert tron.withdraw_enabled is True
    assert tron.withdraw_fee == 1.5
    assert tron.min_withdraw == 10.0
    assert tron.confirmations == 3


def test_public_chain_aliases_are_normalized():
    aliases = {
        "ERC20": "ETH",
        "TRC20": "TRON",
        "BEP20": "BSC",
        "ArbitrumOne": "ARBITRUM",
        "Optimism": "OPTIMISM",
        "AVAXC-Chain": "AVAXC",
        "Aptos": "APTOS",
        "SOL": "SOL",
        "BASE": "BASE",
        "LIGHTNING": "BTCLN",
    }

    for raw, expected in aliases.items():
        assert (
            BitgetNetworkMetadataAdapter
            ._normalize_network_name(raw)
            == expected
        )

def test_coin_is_normalized():
    adapter = BitgetNetworkMetadataAdapter(
        client=FakeClient(),
    )

    result = adapter.describe_networks(
        " usdt "
    )

    assert result["coin"] == "USDT"


def test_unknown_coin_returns_available_empty_metadata():
    adapter = BitgetNetworkMetadataAdapter(
        client=FakeClient(),
    )

    result = adapter.describe_networks(
        "XYZ"
    )

    assert result[
        "network_metadata_available"
    ] is True

    assert result[
        "transfer_verification_available"
    ] is False

    assert result[
        "networks"
    ] == []


def test_failed_fetch_fails_closed():
    adapter = BitgetNetworkMetadataAdapter(
        client=FailedClient(),
    )

    result = adapter.describe_networks(
        "USDT"
    )

    assert result[
        "network_metadata_available"
    ] is False

    assert result[
        "transfer_verification_available"
    ] is False

    assert result[
        "networks"
    ] == []


def test_coin_is_required():
    adapter = BitgetNetworkMetadataAdapter(
        client=FakeClient(),
    )

    with pytest.raises(
        ValueError,
        match="coin is required",
    ):
        adapter.describe_networks("")
