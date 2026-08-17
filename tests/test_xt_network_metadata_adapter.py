import pytest

from exchanges.xt_network_metadata_adapter import (
    XTNetworkMetadataAdapter,
)


class FakeClient:
    def fetch(self):
        return {
            "exchange_id": "xt",
            "fetch_complete": True,
            "reason": None,
            "currencies": [
                {
                    "currency": "usdt",
                    "supportChains": [
                        {
                            "chain": "Tron",
                            "depositEnabled": True,
                            "withdrawEnabled": True,
                            "contract": (
                                "TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t"
                            ),
                            "depositMinAmount": 0.1,
                            "depositFeeRate": 0,
                            "depositConfirmations": 3,
                            "withdrawMinAmount": 10,
                            "withdrawPrecision": 6,
                            "withdrawFeeAmount": 1,
                            "withdrawFeeCurrency": "usdt",
                            "withdrawFeeCurrencyId": 11,
                        },
                        {
                            "chain": "Ethereum",
                            "depositEnabled": True,
                            "withdrawEnabled": False,
                            "contract": (
                                "0xdac17f958d2ee523a2206206994597c13d831ec7"
                            ),
                            "depositMinAmount": 0,
                            "depositFeeRate": 0,
                            "depositConfirmations": 12,
                            "withdrawMinAmount": 10,
                            "withdrawPrecision": 6,
                            "withdrawFeeAmount": 2,
                            "withdrawFeeCurrency": "usdt",
                            "withdrawFeeCurrencyId": 11,
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
    def fetch(self):
        return {
            "exchange_id": "xt",
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
        XTNetworkMetadataAdapter(
            client=None,
        )


def test_describes_xt_networks():
    adapter = XTNetworkMetadataAdapter(
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

    tron = result["networks"][0]

    assert tron.coin == "USDT"
    assert tron.network == "TRX"
    assert tron.deposit_enabled is True
    assert tron.withdraw_enabled is True
    assert tron.confirmations == 3
    assert tron.min_withdraw == 10.0
    assert tron.withdraw_fee == 1.0


def test_xt_networks_use_network_info_contract():
    adapter = XTNetworkMetadataAdapter(
        client=FakeClient(),
    )

    network = (
        adapter.describe_networks(
            "USDT"
        )["networks"][0]
    )

    assert network.coin == "USDT"
    assert network.network == "TRX"
    assert network.min_withdraw == 10.0
    assert network.withdraw_fee == 1.0


def test_disabled_withdrawal_is_preserved():
    adapter = XTNetworkMetadataAdapter(
        client=FakeClient(),
    )

    result = adapter.describe_networks(
        "USDT"
    )

    ethereum = result[
        "networks"
    ][1]

    assert ethereum.deposit_enabled is True
    assert ethereum.withdraw_enabled is False


def test_coin_is_normalized():
    adapter = XTNetworkMetadataAdapter(
        client=FakeClient(),
    )

    result = adapter.describe_networks(
        " usdt "
    )

    assert result["coin"] == "USDT"


def test_unknown_coin_returns_available_empty_metadata():
    adapter = XTNetworkMetadataAdapter(
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
    adapter = XTNetworkMetadataAdapter(
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
    adapter = XTNetworkMetadataAdapter(
        client=FakeClient(),
    )

    with pytest.raises(
        ValueError,
        match="coin is required",
    ):
        adapter.describe_networks("")



def test_xt_common_network_names_are_normalized():
    normalize = (
        XTNetworkMetadataAdapter
        ._normalize_network
    )

    assert normalize(
        "Bitcoin"
    ) == "BTC"

    assert normalize(
        "BNB Smart Chain"
    ) == "BSC"

    assert normalize(
        "Ethereum"
    ) == "ETH"

    assert normalize(
        "Solana"
    ) == "SOL"

    assert normalize(
        "Tron"
    ) == "TRX"

    assert normalize(
        "Arbitrum One"
    ) == "ARBITRUM"

    assert normalize(
        "Polygon POS"
    ) == "MATIC"

    assert normalize(
        "AVAX C-Chain"
    ) == "AVAXC"


def test_xt_unknown_network_name_is_preserved():
    assert (
        XTNetworkMetadataAdapter
        ._normalize_network(
            "Some New Chain"
        )
        == "SOME NEW CHAIN"
    )
