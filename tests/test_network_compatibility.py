from exchanges.network_compatibility import NetworkCompatibility
from exchanges.network_registry import NetworkInfo


def test_finds_shared_network():
    source = [
        NetworkInfo("USDT", "TRC20"),
        NetworkInfo("USDT", "ERC20"),
    ]

    destination = [
        NetworkInfo("USDT", "TRC20"),
        NetworkInfo("USDT", "BEP20"),
    ]

    compatible = NetworkCompatibility.compatible_networks(
        source,
        destination,
    )

    assert len(compatible) == 1
    assert compatible[0].network == "TRC20"


def test_excludes_source_withdraw_disabled():
    source = [
        NetworkInfo(
            "USDT",
            "TRC20",
            withdraw_enabled=False,
        )
    ]

    destination = [
        NetworkInfo("USDT", "TRC20")
    ]

    compatible = NetworkCompatibility.compatible_networks(
        source,
        destination,
    )

    assert compatible == []


def test_excludes_destination_deposit_disabled():
    source = [
        NetworkInfo("USDT", "TRC20")
    ]

    destination = [
        NetworkInfo(
            "USDT",
            "TRC20",
            deposit_enabled=False,
        )
    ]

    compatible = NetworkCompatibility.compatible_networks(
        source,
        destination,
    )

    assert compatible == []


def test_excludes_maintenance_networks():
    source = [
        NetworkInfo(
            "USDT",
            "TRC20",
            maintenance=True,
        )
    ]

    destination = [
        NetworkInfo("USDT", "TRC20")
    ]

    compatible = NetworkCompatibility.compatible_networks(
        source,
        destination,
    )

    assert compatible == []


def test_network_matching_is_case_insensitive():
    source = [
        NetworkInfo("USDT", "trc20")
    ]

    destination = [
        NetworkInfo("USDT", "TRC20")
    ]

    compatible = NetworkCompatibility.compatible_networks(
        source,
        destination,
    )

    assert len(compatible) == 1
