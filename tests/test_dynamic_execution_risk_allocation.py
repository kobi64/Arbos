import pytest

from exchanges.dynamic_execution_risk_allocation import DynamicExecutionRiskAllocation


def test_create_risk_allocator():
    allocator = DynamicExecutionRiskAllocation()

    assert allocator is not None


def test_calculate_test_trade_amount():
    allocator = DynamicExecutionRiskAllocation()

    result = allocator.calculate_allocation(
        capital=10000,
        reliability=96,
        risk_level="low",
    )

    assert result["test_trade"] == 250


def test_calculate_scaled_trade_amount():
    allocator = DynamicExecutionRiskAllocation()

    result = allocator.calculate_allocation(
        capital=10000,
        reliability=96,
        risk_level="low",
    )

    assert result["maximum_trade"] > result["test_trade"]


def test_high_risk_reduces_allocation():
    allocator = DynamicExecutionRiskAllocation()

    result = allocator.calculate_allocation(
        capital=10000,
        reliability=50,
        risk_level="high",
    )

    assert result["maximum_trade"] < 5000


def test_validation_allows_scaling():
    allocator = DynamicExecutionRiskAllocation()

    result = allocator.validate_execution(
        test_trade_success=True
    )

    assert result["approved"] is True


def test_failed_test_trade_blocks_scaling():
    allocator = DynamicExecutionRiskAllocation()

    result = allocator.validate_execution(
        test_trade_success=False
    )

    assert result["approved"] is False


def test_allocation_reason_generated():
    allocator = DynamicExecutionRiskAllocation()

    result = allocator.calculate_allocation(
        capital=5000,
        reliability=90,
        risk_level="medium",
    )

    assert "reason" in result


def test_allocation_history_recorded():
    allocator = DynamicExecutionRiskAllocation()

    allocator.calculate_allocation(
        capital=5000,
        reliability=90,
        risk_level="medium",
    )

    history = allocator.get_history()

    assert len(history) == 2
