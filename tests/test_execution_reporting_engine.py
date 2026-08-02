from exchanges.execution_reporting_engine import ExecutionReportingEngine


def test_create_reporting_engine():

    engine = ExecutionReportingEngine()

    assert engine is not None


def test_create_report():

    engine = ExecutionReportingEngine()

    result = engine.create_report(
        "tx-001",
        100,
        110
    )

    assert result["transaction_id"] == "tx-001"


def test_profit_calculation():

    engine = ExecutionReportingEngine()

    result = engine.create_report(
        "tx-001",
        100,
        110
    )

    assert result["profit"] == 10


def test_negative_profit():

    engine = ExecutionReportingEngine()

    result = engine.create_report(
        "tx-001",
        100,
        90
    )

    assert result["profit"] == -10


def test_variance_calculation():

    engine = ExecutionReportingEngine()

    result = engine.create_report(
        "tx-001",
        100,
        105,
        expected_profit=10
    )

    assert result["variance"] == -5


def test_failed_execution_report():

    engine = ExecutionReportingEngine()

    result = engine.create_failure_report(
        "tx-001",
        "network_timeout"
    )

    assert result["status"] == "FAILED"


def test_report_history():

    engine = ExecutionReportingEngine()

    engine.create_report(
        "tx-001",
        100,
        110
    )

    history = engine.get_history()

    assert len(history) == 1


def test_report_missing_data():

    engine = ExecutionReportingEngine()

    result = engine.create_report(
        "tx-001",
        None,
        100
    )

    assert result["success"] is False
