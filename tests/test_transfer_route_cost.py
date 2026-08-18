import pytest
from exchanges.network_registry import NetworkInfo
from exchanges.transfer_route_cost import TransferRouteCost


def test_selects_lowest_cost_executable_route_within_threshold():
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

    result = TransferRouteCost.evaluate(
        amount=100.0,
        source_networks=source,
        destination_networks=destination,
        max_cost_percent=2.0,
    )

    assert result.executable is True
    assert result.network == "TRC20"
    assert result.withdraw_fee == 1.0
    assert result.cost_percent == 1.0
    assert result.net_amount == 99.0


def test_rejects_route_when_all_network_costs_exceed_threshold():
    source = [
        NetworkInfo(
            "USDT",
            "ERC20",
            withdraw_fee=8.0,
        ),
        NetworkInfo(
            "USDT",
            "TRC20",
            withdraw_fee=6.0,
        ),
    ]

    destination = [
        NetworkInfo("USDT", "ERC20"),
        NetworkInfo("USDT", "TRC20"),
    ]

    result = TransferRouteCost.evaluate(
        amount=100.0,
        source_networks=source,
        destination_networks=destination,
        max_cost_percent=5.0,
    )

    assert result.executable is False
    assert result.reason == "no_economically_acceptable_route"


def test_uses_more_expensive_network_if_cheapest_route_is_infeasible():
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

    result = TransferRouteCost.evaluate(
        amount=50.0,
        source_networks=source,
        destination_networks=destination,
        max_cost_percent=5.0,
    )

    assert result.executable is True
    assert result.network == "BEP20"
    assert result.withdraw_fee == 2.0
    assert result.cost_percent == 4.0
    assert result.net_amount == 48.0


def test_rejects_when_no_compatible_network_exists():
    source = [
        NetworkInfo("USDT", "ERC20"),
    ]

    destination = [
        NetworkInfo("USDT", "TRC20"),
    ]

    result = TransferRouteCost.evaluate(
        amount=100.0,
        source_networks=source,
        destination_networks=destination,
        max_cost_percent=5.0,
    )

    assert result.executable is False
    assert result.reason == "no_compatible_network"


def test_rejects_invalid_amount():
    source = [
        NetworkInfo(
            "USDT",
            "TRC20",
            withdraw_fee=1.0,
        ),
    ]

    destination = [
        NetworkInfo("USDT", "TRC20"),
    ]

    result = TransferRouteCost.evaluate(
        amount=0.0,
        source_networks=source,
        destination_networks=destination,
        max_cost_percent=5.0,
    )

    assert result.executable is False
    assert result.reason == "invalid_amount"


def test_no_compatible_network_does_not_report_zero_withdraw_fee():
    source = [
        NetworkInfo(
            "USDT",
            "ERC20",
            withdraw_fee=5.0,
        ),
    ]

    destination = [
        NetworkInfo(
            "USDT",
            "TRC20",
        ),
    ]

    result = TransferRouteCost.evaluate(
        amount=100.0,
        source_networks=source,
        destination_networks=destination,
        max_cost_percent=10.0,
    )

    assert result.executable is False
    assert result.network is None
    assert result.withdraw_fee is None
    assert result.reason == "no_compatible_network"


def test_unknown_withdraw_fee_does_not_report_zero_cost_route():
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

    result = TransferRouteCost.evaluate(
        amount=100.0,
        source_networks=source,
        destination_networks=destination,
        max_cost_percent=10.0,
    )

    assert result.executable is False
    assert result.network is None
    assert result.withdraw_fee is None
    assert result.reason == (
        "no_economically_acceptable_route"
    )


def test_invalid_amount_does_not_report_zero_withdraw_fee():
    source = [
        NetworkInfo(
            "USDT",
            "TRC20",
            withdraw_fee=1.0,
        ),
    ]

    destination = [
        NetworkInfo(
            "USDT",
            "TRC20",
        ),
    ]

    result = TransferRouteCost.evaluate(
        amount=0.0,
        source_networks=source,
        destination_networks=destination,
        max_cost_percent=10.0,
    )

    assert result.executable is False
    assert result.withdraw_fee is None
    assert result.reason == "invalid_amount"


def test_genuine_zero_fee_route_preserves_zero():
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

    result = TransferRouteCost.evaluate(
        amount=100.0,
        source_networks=source,
        destination_networks=destination,
        max_cost_percent=10.0,
    )

    assert result.executable is True
    assert result.network == "TRC20"
    assert result.withdraw_fee == 0.0
    assert result.cost_percent == 0.0
    assert result.net_amount == 100.0
    assert result.reason == "ok"


def test_failed_cost_route_preserves_uncalculated_values_as_unknown():
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

    result = TransferRouteCost.evaluate(
        amount=100.0,
        source_networks=source,
        destination_networks=destination,
        max_cost_percent=10.0,
    )

    assert result.executable is False
    assert result.cost_percent is None
    assert result.net_amount is None


def test_economically_rejected_route_preserves_result_values_as_unknown():
    source = [
        NetworkInfo(
            "USDT",
            "TRC20",
            withdraw_fee=10.0,
            min_withdraw=1.0,
        ),
    ]

    destination = [
        NetworkInfo(
            "USDT",
            "TRC20",
        ),
    ]

    result = TransferRouteCost.evaluate(
        amount=100.0,
        source_networks=source,
        destination_networks=destination,
        max_cost_percent=5.0,
    )

    assert result.executable is False
    assert result.cost_percent is None
    assert result.net_amount is None
    assert result.reason == (
        "no_economically_acceptable_route"
    )


@pytest.mark.parametrize(
    "amount",
    [
        None,
        "bad",
        float("nan"),
        float("inf"),
        float("-inf"),
        True,
    ],
)
def test_invalid_route_amount_numeric_contract(amount):
    source = [
        NetworkInfo(
            "USDT",
            "TRC20",
            withdraw_fee=1.0,
            min_withdraw=1.0,
        ),
    ]
    destination = [
        NetworkInfo("USDT", "TRC20"),
    ]

    result = TransferRouteCost.evaluate(
        amount=amount,
        source_networks=source,
        destination_networks=destination,
        max_cost_percent=5.0,
    )

    assert result.executable is False
    assert result.reason == "invalid_amount"


@pytest.mark.parametrize(
    "limit",
    [
        None,
        "bad",
        float("nan"),
        float("inf"),
        float("-inf"),
        True,
        -1.0,
    ],
)
def test_invalid_route_cost_limit_numeric_contract(limit):
    source = [
        NetworkInfo(
            "USDT",
            "TRC20",
            withdraw_fee=1.0,
            min_withdraw=1.0,
        ),
    ]
    destination = [
        NetworkInfo("USDT", "TRC20"),
    ]

    result = TransferRouteCost.evaluate(
        amount=100.0,
        source_networks=source,
        destination_networks=destination,
        max_cost_percent=limit,
    )

    assert result.executable is False
    assert result.reason == "invalid_max_cost_percent"
