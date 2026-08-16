from exchanges.network_adapter import ExchangeNetworkAdapter
from exchanges.network_registry import NetworkInfo


def test_normalize_single_network():
    raw = {
        "network": "trc20",
        "deposit_enabled": True,
        "withdraw_enabled": True,
        "maintenance": False,
        "withdraw_fee": "1.0",
        "min_withdraw": "10",
        "confirmations": "20",
    }

    network = ExchangeNetworkAdapter.normalize_network("USDT", raw)

    assert isinstance(network, NetworkInfo)
    assert network.coin == "USDT"
    assert network.network == "TRC20"
    assert network.deposit_enabled is True
    assert network.withdraw_enabled is True
    assert network.maintenance is False
    assert network.withdraw_fee == 1.0
    assert network.min_withdraw == 10.0
    assert network.confirmations == 20


def test_normalize_network_defaults():
    network = ExchangeNetworkAdapter.normalize_network(
        "USDT",
        {"network": "erc20"},
    )

    assert network.network == "ERC20"
    assert network.deposit_enabled is False
    assert network.withdraw_enabled is False
    assert network.maintenance is False
    assert network.withdraw_fee is None
    assert network.min_withdraw is None
    assert network.confirmations == 0


def test_normalize_multiple_networks():
    raw_networks = [
        {
            "network": "trc20",
            "deposit_enabled": True,
            "withdraw_enabled": True,
        },
        {
            "network": "erc20",
            "deposit_enabled": False,
            "withdraw_enabled": True,
        },
    ]

    networks = ExchangeNetworkAdapter.normalize_networks(
        "USDT",
        raw_networks,
    )

    assert len(networks) == 2
    assert networks[0].network == "TRC20"
    assert networks[1].network == "ERC20"
    assert networks[0].deposit_enabled is True
    assert networks[1].deposit_enabled is False
        



def test_explicit_unknown_minimum_withdrawal_is_preserved():
    network = ExchangeNetworkAdapter.normalize_network(
        "USDT",
        {
            "network": "trc20",
            "deposit_enabled": True,
            "withdraw_enabled": True,
            "withdraw_fee": 1.0,
            "min_withdraw": None,
        },
    )

    assert network.min_withdraw is None



def test_missing_withdraw_fee_is_preserved_as_unknown():
    network = ExchangeNetworkAdapter.normalize_network(
        "USDT",
        {
            "network": "trc20",
            "deposit_enabled": True,
            "withdraw_enabled": True,
            "min_withdraw": 10.0,
        },
    )

    assert network.withdraw_fee is None


def test_none_withdraw_fee_is_preserved_as_unknown():
    network = ExchangeNetworkAdapter.normalize_network(
        "USDT",
        {
            "network": "trc20",
            "deposit_enabled": True,
            "withdraw_enabled": True,
            "withdraw_fee": None,
            "min_withdraw": 10.0,
        },
    )

    assert network.withdraw_fee is None


def test_explicit_zero_withdraw_fee_is_preserved():
    network = ExchangeNetworkAdapter.normalize_network(
        "USDT",
        {
            "network": "trc20",
            "deposit_enabled": True,
            "withdraw_enabled": True,
            "withdraw_fee": 0.0,
            "min_withdraw": 10.0,
        },
    )

    assert network.withdraw_fee == 0.0
