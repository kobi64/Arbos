from exchanges.network_registry import NetworkInfo, NetworkRegistry


def test_add_and_get_networks():
    registry = NetworkRegistry()

    registry.add_network(NetworkInfo("USDT", "TRC20"))

    networks = registry.get_networks("USDT")

    assert len(networks) == 1
    assert networks[0].network == "TRC20"


def test_coin_lookup_is_case_insensitive():
    registry = NetworkRegistry()

    registry.add_network(NetworkInfo("usdt", "TRC20"))

    networks = registry.get_networks("UsDt")

    assert len(networks) == 1


def test_executable_networks_excludes_maintenance():
    registry = NetworkRegistry()

    registry.add_network(NetworkInfo("USDT", "TRC20"))
    registry.add_network(
        NetworkInfo("USDT", "ERC20", maintenance=True)
    )

    executable = registry.executable_networks("USDT")

    assert len(executable) == 1
    assert executable[0].network == "TRC20"


def test_executable_networks_requires_deposit_and_withdrawal():
    registry = NetworkRegistry()

    registry.add_network(
        NetworkInfo("USDT", "TRC20", deposit_enabled=False)
    )
    registry.add_network(
        NetworkInfo("USDT", "ERC20", withdraw_enabled=False)
    )
    registry.add_network(NetworkInfo("USDT", "BEP20"))

    executable = registry.executable_networks("USDT")

    assert len(executable) == 1
    assert executable[0].network == "BEP20"


def test_network_info_unknown_minimum_defaults_to_none():
    network = NetworkInfo(
        "USDT",
        "TRC20",
    )

    assert network.min_withdraw is None


def test_network_info_unknown_withdraw_fee_defaults_to_none():
    network = NetworkInfo(
        "USDT",
        "TRC20",
    )

    assert network.withdraw_fee is None


def test_network_info_explicit_zero_withdraw_fee_is_preserved():
    network = NetworkInfo(
        "USDT",
        "TRC20",
        withdraw_fee=0.0,
    )

    assert network.withdraw_fee == 0.0
