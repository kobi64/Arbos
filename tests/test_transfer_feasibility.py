from exchanges.network_registry import NetworkInfo
from exchanges.transfer_feasibility import TransferFeasibility


def test_transfer_is_feasible_when_amount_covers_minimum_and_fee():
    network = NetworkInfo(
        "USDT",
        "TRC20",
        withdraw_fee=1.0,
        min_withdraw=10.0,
    )

    result = TransferFeasibility.evaluate(
        amount=100.0,
        network=network,
    )

    assert result.feasible is True
    assert result.net_amount == 99.0


def test_transfer_rejected_below_minimum_withdrawal():
    network = NetworkInfo(
        "USDT",
        "TRC20",
        withdraw_fee=1.0,
        min_withdraw=10.0,
    )

    result = TransferFeasibility.evaluate(
        amount=5.0,
        network=network,
    )

    assert result.feasible is False


def test_transfer_rejected_when_fee_consumes_amount():
    network = NetworkInfo(
        "USDT",
        "TRC20",
        withdraw_fee=10.0,
        min_withdraw=0.0,
    )

    result = TransferFeasibility.evaluate(
        amount=10.0,
        network=network,
    )

    assert result.feasible is False


def test_transfer_rejected_when_network_in_maintenance():
    network = NetworkInfo(
        "USDT",
        "TRC20",
        maintenance=True,
    )

    result = TransferFeasibility.evaluate(
        amount=100.0,
        network=network,
    )

    assert result.feasible is False


def test_transfer_rejected_when_withdrawals_disabled():
    network = NetworkInfo(
        "USDT",
        "TRC20",
        withdraw_enabled=False,
    )

    result = TransferFeasibility.evaluate(
        amount=100.0,
        network=network,
    )

    assert result.feasible is False


def test_transfer_rejected_when_minimum_withdrawal_unknown():
    network = NetworkInfo(
        "USDT",
        "TRC20",
        withdraw_fee=1.0,
        min_withdraw=None,
    )

    result = TransferFeasibility.evaluate(
        amount=100.0,
        network=network,
    )

    assert result.feasible is False
    assert result.net_amount is None
    assert result.reason == (
        "minimum_withdrawal_unknown"
    )


def test_maintenance_preserves_uncalculated_net_amount_as_unknown():
    network = NetworkInfo(
        "USDT",
        "TRC20",
        withdraw_fee=1.0,
        min_withdraw=1.0,
        maintenance=True,
    )

    result = TransferFeasibility.evaluate(
        amount=100.0,
        network=network,
    )

    assert result.feasible is False
    assert result.net_amount is None
    assert result.reason == "network_in_maintenance"


def test_disabled_withdrawal_preserves_uncalculated_net_amount_as_unknown():
    network = NetworkInfo(
        "USDT",
        "TRC20",
        withdraw_fee=1.0,
        min_withdraw=1.0,
        withdraw_enabled=False,
    )

    result = TransferFeasibility.evaluate(
        amount=100.0,
        network=network,
    )

    assert result.feasible is False
    assert result.net_amount is None
    assert result.reason == "withdrawals_disabled"


def test_below_minimum_preserves_uncalculated_net_amount_as_unknown():
    network = NetworkInfo(
        "USDT",
        "TRC20",
        withdraw_fee=1.0,
        min_withdraw=100.0,
    )

    result = TransferFeasibility.evaluate(
        amount=50.0,
        network=network,
    )

    assert result.feasible is False
    assert result.net_amount is None
    assert result.reason == "below_minimum_withdrawal"


def test_unknown_fee_preserves_uncalculated_net_amount_as_unknown():
    network = NetworkInfo(
        "USDT",
        "TRC20",
        withdraw_fee=None,
        min_withdraw=1.0,
    )

    result = TransferFeasibility.evaluate(
        amount=100.0,
        network=network,
    )

    assert result.feasible is False
    assert result.net_amount is None
    assert result.reason == "withdrawal_fee_unknown"


def test_fee_consumes_amount_preserves_calculated_zero():
    network = NetworkInfo(
        "USDT",
        "TRC20",
        withdraw_fee=100.0,
        min_withdraw=0.0,
    )

    result = TransferFeasibility.evaluate(
        amount=100.0,
        network=network,
    )

    assert result.feasible is False
    assert result.net_amount == 0.0
    assert result.reason == (
        "withdrawal_fee_consumes_amount"
    )
