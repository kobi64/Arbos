from exchanges.network_registry import NetworkInfo
from exchanges.route_validator import RouteValidator


def test_route_is_executable_with_shared_network():
    source = [
        NetworkInfo("USDT", "TRC20"),
        NetworkInfo("USDT", "ERC20"),
    ]

    destination = [
        NetworkInfo("USDT", "TRC20"),
    ]

    result = RouteValidator.validate_transfer_route(
        source,
        destination,
    )

    assert result.executable is True
    assert result.network == "TRC20"


def test_route_is_not_executable_without_shared_network():
    source = [
        NetworkInfo("USDT", "ERC20"),
    ]

    destination = [
        NetworkInfo("USDT", "TRC20"),
    ]

    result = RouteValidator.validate_transfer_route(
        source,
        destination,
    )

    assert result.executable is False
    assert result.network is None


def test_route_rejects_withdraw_disabled_source():
    source = [
        NetworkInfo(
            "USDT",
            "TRC20",
            withdraw_enabled=False,
        )
    ]

    destination = [
        NetworkInfo("USDT", "TRC20"),
    ]

    result = RouteValidator.validate_transfer_route(
        source,
        destination,
    )

    assert result.executable is False


def test_route_rejects_deposit_disabled_destination():
    source = [
        NetworkInfo("USDT", "TRC20"),
    ]

    destination = [
        NetworkInfo(
            "USDT",
            "TRC20",
            deposit_enabled=False,
        )
    ]

    result = RouteValidator.validate_transfer_route(
        source,
        destination,
    )

    assert result.executable is False


def test_route_returns_lowest_fee_compatible_network():
    source = [
        NetworkInfo(
            "USDT",
            "ERC20",
            withdraw_fee=8.0,
        ),
        NetworkInfo(
            "USDT",
            "TRC20",
            withdraw_fee=1.0,
        ),
    ]

    destination = [
        NetworkInfo("USDT", "ERC20"),
        NetworkInfo("USDT", "TRC20"),
    ]

    result = RouteValidator.validate_transfer_route(
        source,
        destination,
    )

    assert result.executable is True
    assert result.network == "TRC20"
    assert result.withdraw_fee == 1.0
