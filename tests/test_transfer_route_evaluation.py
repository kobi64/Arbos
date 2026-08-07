from exchanges.network_registry import NetworkInfo
from exchanges.transfer_route_evaluation import TransferRouteEvaluation


def test_selects_executable_lowest_fee_route():
    source = [
        NetworkInfo(
            "USDT",
            "ERC20",
            withdraw_fee=8.0,
            min_withdraw=10.0,
        ),
        NetworkInfo(
            "USDT",
            "TRC20",
            withdraw_fee=1.0,
            min_withdraw=10.0,
        ),
    ]

    destination = [
        NetworkInfo("USDT", "ERC20"),
        NetworkInfo("USDT", "TRC20"),
    ]

    result = TransferRouteEvaluation.evaluate(
        amount=100.0,
        source_networks=source,
        destination_networks=destination,
    )

    assert result.executable is True
    assert result.network == "TRC20"
    assert result.withdraw_fee == 1.0
    assert result.net_amount == 99.0


def test_rejects_route_when_no_compatible_network_exists():
    source = [
        NetworkInfo("USDT", "ERC20"),
    ]

    destination = [
        NetworkInfo("USDT", "TRC20"),
    ]

    result = TransferRouteEvaluation.evaluate(
        amount=100.0,
        source_networks=source,
        destination_networks=destination,
    )

    assert result.executable is False
    assert result.network is None


def test_rejects_route_when_amount_below_minimum():
    source = [
        NetworkInfo(
            "USDT",
            "TRC20",
            withdraw_fee=1.0,
            min_withdraw=50.0,
        ),
    ]

    destination = [
        NetworkInfo("USDT", "TRC20"),
    ]

    result = TransferRouteEvaluation.evaluate(
        amount=25.0,
        source_networks=source,
        destination_networks=destination,
    )

    assert result.executable is False


def test_uses_next_compatible_network_if_cheapest_is_not_feasible():
    source = [
        NetworkInfo(
            "USDT",
            "TRC20",
            withdraw_fee=1.0,
            min_withdraw=100.0,
        ),
        NetworkInfo(
            "USDT",
            "BEP20",
            withdraw_fee=2.0,
            min_withdraw=10.0,
        ),
    ]

    destination = [
        NetworkInfo("USDT", "TRC20"),
        NetworkInfo("USDT", "BEP20"),
    ]

    result = TransferRouteEvaluation.evaluate(
        amount=50.0,
        source_networks=source,
        destination_networks=destination,
    )

    assert result.executable is True
    assert result.network == "BEP20"
    assert result.withdraw_fee == 2.0
    assert result.net_amount == 48.0


def test_rejects_route_when_all_compatible_networks_are_infeasible():
    source = [
        NetworkInfo(
            "USDT",
            "TRC20",
            withdraw_fee=60.0,
            min_withdraw=0.0,
        ),
        NetworkInfo(
            "USDT",
            "BEP20",
            withdraw_fee=55.0,
            min_withdraw=0.0,
        ),
    ]

    destination = [
        NetworkInfo("USDT", "TRC20"),
        NetworkInfo("USDT", "BEP20"),
    ]

    result = TransferRouteEvaluation.evaluate(
        amount=50.0,
        source_networks=source,
        destination_networks=destination,
    )

    assert result.executable is False


def test_unknown_withdraw_fee_is_not_executable():
    source_networks = [
        NetworkInfo(
            coin="ETH",
            network="ETH",
            deposit_enabled=True,
            withdraw_enabled=True,
            withdraw_fee=None,
        ),
    ]

    destination_networks = [
        NetworkInfo(
            coin="ETH",
            network="ETH",
            deposit_enabled=True,
            withdraw_enabled=True,
            withdraw_fee=0.0,
        ),
    ]

    result = TransferRouteEvaluation.evaluate(
        amount=1.0,
        source_networks=source_networks,
        destination_networks=destination_networks,
    )

    assert result.executable is False
    assert result.reason == "no_feasible_network"
