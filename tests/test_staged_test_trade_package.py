import pytest

from core.staged_test_trade_package import (
    StagedTestTradePackage,
)


def ready_result():
    return {
        "ready_for_staged_execution": True,
        "reason": "ready_for_staged_execution",
        "route": {
            "route_id": "DIRECT-ETH",
            "route_type": "direct_cross_exchange",
            "coin_asset": "ETH",
            "source_exchange": "kucoin",
            "destination_exchange": "gate",
            "net_profit": 1.0,
            "net_profit_percent": 1.0,
        },
        "live_order_submitted": False,
    }


def test_builds_small_validation_trade_package():
    builder = StagedTestTradePackage()

    result = builder.prepare(
        readiness_result=ready_result(),
        available_capital=10000.0,
        reliability=96.0,
        risk_level="low",
        estimated_fees=0.50,
        slippage_allowance=0.25,
    )

    assert result["prepared"] is True
    assert result["test_trade_amount"] == 250.0
    assert result["trade_package"]["ready"] is True
    assert (
        result["trade_package"]["trade"]["trade_amount"]
        == 250.0
    )


def test_small_capital_uses_five_percent_test_trade():
    builder = StagedTestTradePackage()

    result = builder.prepare(
        readiness_result=ready_result(),
        available_capital=1000.0,
        reliability=96.0,
        risk_level="low",
        estimated_fees=0.10,
        slippage_allowance=0.05,
    )

    assert result["test_trade_amount"] == 50.0


def test_preserves_route_identity():
    builder = StagedTestTradePackage()

    result = builder.prepare(
        readiness_result=ready_result(),
        available_capital=10000.0,
        reliability=96.0,
        risk_level="low",
        estimated_fees=0.50,
        slippage_allowance=0.25,
    )

    assert result["route_id"] == "DIRECT-ETH"
    assert result["route_type"] == "direct_cross_exchange"


def test_requires_manual_approval_and_submits_nothing():
    builder = StagedTestTradePackage()

    result = builder.prepare(
        readiness_result=ready_result(),
        available_capital=10000.0,
        reliability=96.0,
        risk_level="low",
        estimated_fees=0.50,
        slippage_allowance=0.25,
    )

    assert result["manual_approval_required"] is True
    assert result["approval_granted"] is False
    assert result["live_order_submitted"] is False


def test_not_ready_result_blocks_package_creation():
    builder = StagedTestTradePackage()

    readiness = ready_result()
    readiness["ready_for_staged_execution"] = False

    result = builder.prepare(
        readiness_result=readiness,
        available_capital=10000.0,
        reliability=96.0,
        risk_level="low",
        estimated_fees=0.50,
        slippage_allowance=0.25,
    )

    assert result["prepared"] is False
    assert result["reason"] == "staged_execution_not_ready"
    assert result["live_order_submitted"] is False


def test_missing_route_blocks_package_creation():
    builder = StagedTestTradePackage()

    readiness = ready_result()
    readiness["route"] = None

    result = builder.prepare(
        readiness_result=readiness,
        available_capital=10000.0,
        reliability=96.0,
        risk_level="low",
        estimated_fees=0.50,
        slippage_allowance=0.25,
    )

    assert result["prepared"] is False
    assert result["reason"] == "route_required"


def test_missing_readiness_result_is_rejected():
    builder = StagedTestTradePackage()

    with pytest.raises(
        ValueError,
        match="readiness_result is required",
    ):
        builder.prepare(
            readiness_result=None,
            available_capital=10000.0,
            reliability=96.0,
            risk_level="low",
            estimated_fees=0.50,
            slippage_allowance=0.25,
        )
