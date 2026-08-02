import pytest

from exchanges.execution_reconciliation import ExecutionReconciliation


def test_create_reconciliation_engine():
    engine = ExecutionReconciliation(
        execution_id="ARB-001"
    )

    assert engine is not None


def test_record_expected_result():
    engine = ExecutionReconciliation(
        execution_id="ARB-002"
    )

    result = engine.set_expected(
        starting_balance=1000,
        expected_balance=1025,
    )

    assert result["expected_balance"] == 1025


def test_record_actual_result():
    engine = ExecutionReconciliation(
        execution_id="ARB-003"
    )

    result = engine.set_actual(
        final_balance=1024.72,
    )

    assert result["actual_balance"] == 1024.72


def test_successful_settlement_match():
    engine = ExecutionReconciliation(
        execution_id="ARB-004"
    )

    engine.set_expected(
        starting_balance=1000,
        expected_balance=1025,
    )

    engine.set_actual(
        final_balance=1025,
    )

    result = engine.reconcile()

    assert result["status"] == "settled"


def test_detect_balance_difference():
    engine = ExecutionReconciliation(
        execution_id="ARB-005"
    )

    engine.set_expected(
        starting_balance=1000,
        expected_balance=1025,
    )

    engine.set_actual(
        final_balance=1024.50,
    )

    result = engine.reconcile()

    assert result["status"] == "difference"


def test_calculate_realised_profit():
    engine = ExecutionReconciliation(
        execution_id="ARB-006"
    )

    engine.set_expected(
        starting_balance=1000,
        expected_balance=1025,
    )

    engine.set_actual(
        final_balance=1024.72,
    )

    result = engine.calculate_profit()

    assert result["profit"] == 24.72


def test_include_fees():
    engine = ExecutionReconciliation(
        execution_id="ARB-007"
    )

    engine.set_expected(
        starting_balance=1000,
        expected_balance=1025,
    )

    engine.set_actual(
        final_balance=1025,
    )

    result = engine.add_fees(
        fees=1.50
    )

    assert result["net_profit"] == 23.50


def test_reconciliation_history_recorded():
    engine = ExecutionReconciliation(
        execution_id="ARB-008"
    )

    engine.set_actual(
        final_balance=1000,
    )

    history = engine.get_history()

    assert len(history) == 2
