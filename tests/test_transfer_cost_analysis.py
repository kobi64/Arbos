from exchanges.network_registry import NetworkInfo
from exchanges.transfer_cost_analysis import TransferCostAnalysis


def test_calculates_transfer_cost_percentage():
    network = NetworkInfo(
        "USDT",
        "TRC20",
        withdraw_fee=1.0,
    )

    result = TransferCostAnalysis.evaluate(
        amount=100.0,
        network=network,
        max_cost_percent=2.0,
    )

    assert result.acceptable is True
    assert result.withdraw_fee == 1.0
    assert result.cost_percent == 1.0
    assert result.net_amount == 99.0


def test_rejects_transfer_cost_above_threshold():
    network = NetworkInfo(
        "USDT",
        "ERC20",
        withdraw_fee=8.0,
    )

    result = TransferCostAnalysis.evaluate(
        amount=100.0,
        network=network,
        max_cost_percent=5.0,
    )

    assert result.acceptable is False
    assert result.cost_percent == 8.0
    assert result.reason == "transfer_cost_too_high"


def test_accepts_transfer_cost_exactly_at_threshold():
    network = NetworkInfo(
        "USDT",
        "TRC20",
        withdraw_fee=2.0,
    )

    result = TransferCostAnalysis.evaluate(
        amount=100.0,
        network=network,
        max_cost_percent=2.0,
    )

    assert result.acceptable is True
    assert result.cost_percent == 2.0


def test_rejects_zero_transfer_amount():
    network = NetworkInfo(
        "USDT",
        "TRC20",
        withdraw_fee=1.0,
    )

    result = TransferCostAnalysis.evaluate(
        amount=0.0,
        network=network,
        max_cost_percent=2.0,
    )

    assert result.acceptable is False
    assert result.reason == "invalid_amount"


def test_rejects_negative_transfer_amount():
    network = NetworkInfo(
        "USDT",
        "TRC20",
        withdraw_fee=1.0,
    )

    result = TransferCostAnalysis.evaluate(
        amount=-100.0,
        network=network,
        max_cost_percent=2.0,
    )

    assert result.acceptable is False
    assert result.reason == "invalid_amount"


def test_rejects_fee_that_consumes_transfer():
    network = NetworkInfo(
        "USDT",
        "ERC20",
        withdraw_fee=100.0,
    )

    result = TransferCostAnalysis.evaluate(
        amount=100.0,
        network=network,
        max_cost_percent=100.0,
    )

    assert result.acceptable is False
    assert result.net_amount == 0.0
    assert result.reason == "fee_consumes_amount"


def test_unknown_withdraw_fee_is_not_acceptable():
    network = NetworkInfo(
        coin="USDT",
        network="TRC20",
        withdraw_fee=None,
        min_withdraw=1.0,
    )

    result = TransferCostAnalysis.evaluate(
        amount=100.0,
        network=network,
        max_cost_percent=5.0,
    )

    assert result.acceptable is False
    assert result.withdraw_fee is None
    assert result.net_amount == 0.0
    assert result.reason == "withdrawal_fee_unknown"


def test_result_type_declares_withdraw_fee_optional():
    from typing import get_type_hints

    from exchanges.transfer_cost_analysis import (
        TransferCostAnalysisResult,
    )

    hints = get_type_hints(
        TransferCostAnalysisResult
    )

    assert (
        str(hints["withdraw_fee"])
        in {
            "typing.Optional[float]",
            "float | None",
        }
    )


def test_genuine_zero_withdraw_fee_remains_numeric_zero():
    network = NetworkInfo(
        coin="USDT",
        network="TRC20",
        withdraw_fee=0.0,
        min_withdraw=1.0,
    )

    result = TransferCostAnalysis.evaluate(
        amount=100.0,
        network=network,
        max_cost_percent=5.0,
    )

    assert result.acceptable is True
    assert result.withdraw_fee == 0.0
    assert result.cost_percent == 0.0
    assert result.net_amount == 100.0
    assert result.reason == "ok"
