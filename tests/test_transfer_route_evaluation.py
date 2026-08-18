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


def test_no_feasible_network_preserves_failure_diagnostics():
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
            withdraw_fee=None,
            min_withdraw=0.0,
        ),
    ]

    destination = [
        NetworkInfo(
            "USDT",
            "TRC20",
        ),
        NetworkInfo(
            "USDT",
            "BEP20",
        ),
    ]

    result = TransferRouteEvaluation.evaluate(
        amount=50.0,
        source_networks=source,
        destination_networks=destination,
    )

    assert result.executable is False
    assert result.reason == "no_feasible_network"

    diagnostics = result.feasibility_diagnostics

    assert diagnostics is not None
    assert diagnostics[
        "compatible_network_count"
    ] == 2
    assert diagnostics[
        "failed_network_count"
    ] == 2

    assert diagnostics[
        "failures_by_reason"
    ] == {
        "below_minimum_withdrawal": 1,
        "withdrawal_fee_unknown": 1,
    }

    assert diagnostics["failed_networks"] == [
        {
            "network": "TRC20",
            "reason": "below_minimum_withdrawal",
            "withdraw_fee": 1.0,
            "min_withdraw": 100.0,
            "maintenance": False,
            "withdraw_enabled": True,
            "amount": 50.0,
        },
        {
            "network": "BEP20",
            "reason": "withdrawal_fee_unknown",
            "withdraw_fee": None,
            "min_withdraw": 0.0,
            "maintenance": False,
            "withdraw_enabled": True,
            "amount": 50.0,
        },
    ]


def test_successful_route_does_not_require_failure_diagnostics():
    source = [
        NetworkInfo(
            "USDT",
            "TRC20",
            withdraw_fee=1.0,
            min_withdraw=10.0,
        ),
    ]

    destination = [
        NetworkInfo(
            "USDT",
            "TRC20",
        ),
    ]

    result = TransferRouteEvaluation.evaluate(
        amount=100.0,
        source_networks=source,
        destination_networks=destination,
    )

    assert result.executable is True
    assert result.reason == "ok"
    assert result.feasibility_diagnostics is None


def test_no_compatible_network_has_no_feasibility_diagnostics():
    source = [
        NetworkInfo(
            "USDT",
            "ERC20",
        ),
    ]

    destination = [
        NetworkInfo(
            "USDT",
            "TRC20",
        ),
    ]

    result = TransferRouteEvaluation.evaluate(
        amount=100.0,
        source_networks=source,
        destination_networks=destination,
    )

    assert result.executable is False
    assert result.reason == "no_compatible_network"
    assert result.feasibility_diagnostics is None


def test_no_compatible_network_does_not_report_zero_withdraw_fee():
    source = [
        NetworkInfo(
            "USDT",
            "ERC20",
            withdraw_fee=5.0,
            min_withdraw=1.0,
        ),
    ]

    destination = [
        NetworkInfo(
            "USDT",
            "TRC20",
        ),
    ]

    result = TransferRouteEvaluation.evaluate(
        amount=100.0,
        source_networks=source,
        destination_networks=destination,
    )

    assert result.executable is False
    assert result.network is None
    assert result.withdraw_fee is None


def test_unknown_withdraw_fee_remains_unknown_on_failed_route():
    source = [
        NetworkInfo(
            "USDT",
            "TRC20",
            withdraw_fee=None,
            min_withdraw=1.0,
        ),
    ]

    destination = [
        NetworkInfo(
            "USDT",
            "TRC20",
        ),
    ]

    result = TransferRouteEvaluation.evaluate(
        amount=100.0,
        source_networks=source,
        destination_networks=destination,
    )

    assert result.executable is False
    assert result.withdraw_fee is None

    diagnostics = result.feasibility_diagnostics

    assert diagnostics is not None
    assert diagnostics[
        "failures_by_reason"
    ] == {
        "withdrawal_fee_unknown": 1,
    }


def test_genuine_zero_fee_executable_route_preserves_zero():
    source = [
        NetworkInfo(
            "USDT",
            "TRC20",
            withdraw_fee=0.0,
            min_withdraw=1.0,
        ),
    ]

    destination = [
        NetworkInfo(
            "USDT",
            "TRC20",
        ),
    ]

    result = TransferRouteEvaluation.evaluate(
        amount=100.0,
        source_networks=source,
        destination_networks=destination,
    )

    assert result.executable is True
    assert result.network == "TRC20"
    assert result.withdraw_fee == 0.0
    assert result.net_amount == 100.0
