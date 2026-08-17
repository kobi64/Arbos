import pytest

from exchanges.coinex_network_metadata_adapter import (
    CoinExNetworkMetadataAdapter,
)


class FakeClient:
    def fetch_currency_metadata(
        self,
        currency,
    ):
        return {
            "asset": {
                "ccy": "USDT",
                "deposit_enabled": True,
                "withdraw_enabled": True,
                "inter_transfer_enabled": True,
                "is_st": False,
            },
            "chains": [
                {
                    "chain": "BSC",
                    "min_deposit_amount": "0.2",
                    "min_withdraw_amount": "2",
                    "deposit_enabled": True,
                    "withdraw_enabled": True,
                    "deposit_delay_minutes": 0,
                    "safe_confirmations": 12,
                    "irreversible_confirmations": 30,
                    "deflation_rate": "0",
                    "withdrawal_fee": "0.0065",
                    "withdrawal_precision": 8,
                    "memo": "",
                    "is_memo_required_for_deposit": False,
                    "explorer_asset_url": (
                        "https://bscscan.com/token/"
                        "0x55d398326f99059ff775485246999027b3197955"
                    ),
                },
                {
                    "chain": "PLASMA",
                    "min_deposit_amount": "0.2",
                    "min_withdraw_amount": "0.6",
                    "deposit_enabled": True,
                    "withdraw_enabled": False,
                    "deposit_delay_minutes": 0,
                    "safe_confirmations": 300,
                    "irreversible_confirmations": 600,
                    "deflation_rate": "0",
                    "withdrawal_fee": "0.000039",
                    "withdrawal_precision": 6,
                    "memo": "",
                    "is_memo_required_for_deposit": False,
                    "explorer_asset_url": (
                        "https://plasmascan.to/token/"
                        "0xb8ce59fc3717ada4c02eadf9682a9e934f625ebb"
                    ),
                },
                {
                    "chain": "TON",
                    "min_deposit_amount": "0.22",
                    "min_withdraw_amount": "6",
                    "deposit_enabled": True,
                    "withdraw_enabled": True,
                    "deposit_delay_minutes": 0,
                    "safe_confirmations": 100,
                    "irreversible_confirmations": 150,
                    "deflation_rate": "0",
                    "withdrawal_fee": "0.22",
                    "withdrawal_precision": 6,
                    "memo": "Memo/Comment",
                    "is_memo_required_for_deposit": True,
                    "explorer_asset_url": (
                        "https://tonviewer.com/"
                        "EQCxE6mUtQJKFnGfaROTKOt1lZbDiiX1kCixRv7Nw2Id_sDs"
                    ),
                },
            ],
        }


class FailedClient:
    def fetch_currency_metadata(
        self,
        currency,
    ):
        raise RuntimeError(
            "CoinEx metadata unavailable"
        )


def test_client_is_required():
    with pytest.raises(
        ValueError,
        match="client is required",
    ):
        CoinExNetworkMetadataAdapter(
            client=None,
        )


def test_describes_coinex_networks():
    adapter = CoinExNetworkMetadataAdapter(
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
    ) == 3

    bsc = result["networks"][0]

    assert bsc.coin == "USDT"
    assert bsc.network == "BSC"
    assert bsc.deposit_enabled is True
    assert bsc.withdraw_enabled is True
    assert bsc.maintenance is False
    assert bsc.min_withdraw == 2.0
    assert bsc.withdraw_fee == 0.0065
    assert bsc.confirmations == 12


def test_disabled_withdrawal_is_preserved():
    adapter = CoinExNetworkMetadataAdapter(
        client=FakeClient(),
    )

    result = adapter.describe_networks(
        "USDT"
    )

    plasma = result[
        "networks"
    ][1]

    assert plasma.network == "PLASMA"
    assert plasma.deposit_enabled is True
    assert plasma.withdraw_enabled is False


def test_coinex_common_network_names_are_normalized():
    normalize = (
        CoinExNetworkMetadataAdapter
        ._normalize_network_name
    )

    assert normalize(
        "ERC20"
    ) == "ETH"

    assert normalize(
        "TRC20"
    ) == "TRX"

    assert normalize(
        "BEP20"
    ) == "BSC"

    assert normalize(
        "AVA_C"
    ) == "AVAXC"

    assert normalize(
        "SOL"
    ) == "SOL"

    assert normalize(
        "BTC"
    ) == "BTC"

    assert normalize(
        "PLASMA"
    ) == "PLASMA"


def test_coinex_unknown_network_name_is_preserved():
    assert (
        CoinExNetworkMetadataAdapter
        ._normalize_network_name(
            "NEWCHAIN"
        )
        == "NEWCHAIN"
    )

def test_currency_is_normalized():
    adapter = CoinExNetworkMetadataAdapter(
        client=FakeClient(),
    )

    result = adapter.describe_networks(
        " usdt "
    )

    assert result["coin"] == "USDT"


def test_failed_fetch_fails_closed():
    adapter = CoinExNetworkMetadataAdapter(
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

    assert result["networks"] == []


def test_coin_is_required():
    adapter = CoinExNetworkMetadataAdapter(
        client=FakeClient(),
    )

    with pytest.raises(
        ValueError,
        match="coin is required",
    ):
        adapter.describe_networks("")


def test_coinex_networks_use_network_info_contract():
    from exchanges.network_registry import (
        NetworkInfo,
    )

    adapter = CoinExNetworkMetadataAdapter(
        client=FakeClient(),
    )

    networks = adapter.get_networks(
        "USDT"
    )

    assert len(networks) == 3

    assert all(
        isinstance(
            network,
            NetworkInfo,
        )
        for network in networks
    )

    bsc = networks[0]

    assert bsc.coin == "USDT"
    assert bsc.network == "BSC"
    assert bsc.deposit_enabled is True
    assert bsc.withdraw_enabled is True
    assert bsc.maintenance is False
    assert bsc.withdraw_fee == 0.0065
    assert bsc.min_withdraw == 2.0
    assert bsc.confirmations == 12


def test_coinex_network_info_preserves_disabled_withdrawal():
    adapter = CoinExNetworkMetadataAdapter(
        client=FakeClient(),
    )

    networks = adapter.get_networks(
        "USDT"
    )

    plasma = networks[1]

    assert plasma.network == "PLASMA"
    assert plasma.deposit_enabled is True
    assert plasma.withdraw_enabled is False
    assert plasma.maintenance is False
    assert plasma.withdraw_fee == 0.000039
    assert plasma.min_withdraw == 0.6
    assert plasma.confirmations == 300


def test_coinex_networks_use_network_info_contract():
    from exchanges.network_registry import (
        NetworkInfo,
    )

    adapter = CoinExNetworkMetadataAdapter(
        client=FakeClient(),
    )

    networks = adapter.get_networks(
        "USDT"
    )

    assert len(networks) == 3

    assert all(
        isinstance(
            network,
            NetworkInfo,
        )
        for network in networks
    )

    bsc = networks[0]

    assert bsc.coin == "USDT"
    assert bsc.network == "BSC"
    assert bsc.deposit_enabled is True
    assert bsc.withdraw_enabled is True
    assert bsc.maintenance is False
    assert bsc.withdraw_fee == 0.0065
    assert bsc.min_withdraw == 2.0
    assert bsc.confirmations == 12


def test_coinex_network_info_preserves_disabled_withdrawal():
    adapter = CoinExNetworkMetadataAdapter(
        client=FakeClient(),
    )

    networks = adapter.get_networks(
        "USDT"
    )

    plasma = networks[1]

    assert plasma.network == "PLASMA"
    assert plasma.deposit_enabled is True
    assert plasma.withdraw_enabled is False
    assert plasma.maintenance is False
    assert plasma.withdraw_fee == 0.000039
    assert plasma.min_withdraw == 0.6
    assert plasma.confirmations == 300
