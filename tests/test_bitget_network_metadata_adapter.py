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

    assert result[
        "networks"
    ][0][
        "network"
    ] == "ERC20"

    assert result[
        "networks"
    ][0][
        "withdraw_enabled"
    ] is True

    assert result[
        "networks"
    ][0][
        "deposit_enabled"
    ] is True

    assert result[
        "networks"
    ][0][
        "withdraw_fee"
    ] == 0.8


def test_contract_and_confirmation_metadata_is_preserved():
    adapter = BitgetNetworkMetadataAdapter(
        client=FakeClient(),
    )

    result = adapter.describe_networks(
        "USDT"
    )

    erc20 = result[
        "networks"
    ][0]

    assert erc20[
        "deposit_confirmations"
    ] == 12

    assert erc20[
        "withdraw_confirmations"
    ] == 96

    assert erc20[
        "minimum_deposit"
    ] == 0.5

    assert erc20[
        "minimum_withdrawal"
    ] == 10.0

    assert erc20[
        "contract_address"
    ].startswith("0xdac17")


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
