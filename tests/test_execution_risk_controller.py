import pytest

from exchanges.execution_risk_controller import ExecutionRiskController


def test_create_risk_controller():
    controller = ExecutionRiskController()

    assert controller is not None


def test_approve_valid_execution():
    controller = ExecutionRiskController()

    result = controller.validate_execution(
        trade_size=100,
        expected_profit=5,
        liquidity=1000000,
        slippage=0.5,
        route_valid=True,
        approval_status="approved",
    )

    assert result["status"] == "approved"


def test_reject_trade_size_too_large():
    controller = ExecutionRiskController(
        max_trade_size=1000
    )

    result = controller.validate_execution(
        trade_size=5000,
        expected_profit=100,
        liquidity=1000000,
        slippage=0.5,
        route_valid=True,
        approval_status="approved",
    )

    assert result["status"] == "rejected"
    assert result["reason"] == "trade_size_exceeded"


def test_reject_low_profit():
    controller = ExecutionRiskController(
        min_profit=10
    )

    result = controller.validate_execution(
        trade_size=100,
        expected_profit=2,
        liquidity=1000000,
        slippage=0.5,
        route_valid=True,
        approval_status="approved",
    )

    assert result["status"] == "rejected"
    assert result["reason"] == "profit_below_threshold"


def test_reject_insufficient_liquidity():
    controller = ExecutionRiskController(
        min_liquidity=500000
    )

    result = controller.validate_execution(
        trade_size=100,
        expected_profit=20,
        liquidity=1000,
        slippage=0.5,
        route_valid=True,
        approval_status="approved",
    )

    assert result["status"] == "rejected"
    assert result["reason"] == "insufficient_liquidity"


def test_reject_slippage_too_high():
    controller = ExecutionRiskController(
        max_slippage=1.0
    )

    result = controller.validate_execution(
        trade_size=100,
        expected_profit=20,
        liquidity=1000000,
        slippage=5.0,
        route_valid=True,
        approval_status="approved",
    )

    assert result["status"] == "rejected"
    assert result["reason"] == "slippage_exceeded"


def test_reject_invalid_route():
    controller = ExecutionRiskController()

    result = controller.validate_execution(
        trade_size=100,
        expected_profit=20,
        liquidity=1000000,
        slippage=0.5,
        route_valid=False,
        approval_status="approved",
    )

    assert result["status"] == "rejected"
    assert result["reason"] == "invalid_route"


def test_reject_missing_approval():
    controller = ExecutionRiskController()

    result = controller.validate_execution(
        trade_size=100,
        expected_profit=20,
        liquidity=1000000,
        slippage=0.5,
        route_valid=True,
        approval_status="pending",
    )

    assert result["status"] == "rejected"
    assert result["reason"] == "approval_required"
