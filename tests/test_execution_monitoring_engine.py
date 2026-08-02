from exchanges.execution_monitoring_engine import ExecutionMonitoringEngine


def test_create_monitor():

    monitor = ExecutionMonitoringEngine()

    assert monitor is not None


def test_register_transaction():

    monitor = ExecutionMonitoringEngine()

    result = monitor.register_transaction(
        "tx-001"
    )

    assert result["transaction_id"] == "tx-001"


def test_initial_monitor_status():

    monitor = ExecutionMonitoringEngine()

    result = monitor.register_transaction(
        "tx-001"
    )

    assert result["status"] == "MONITORING"


def test_update_completed():

    monitor = ExecutionMonitoringEngine()

    monitor.register_transaction(
        "tx-001"
    )

    result = monitor.update_status(
        "tx-001",
        "COMPLETED"
    )

    assert result["status"] == "COMPLETED"


def test_update_failed():

    monitor = ExecutionMonitoringEngine()

    monitor.register_transaction(
        "tx-001"
    )

    result = monitor.update_status(
        "tx-001",
        "FAILED"
    )

    assert result["status"] == "FAILED"


def test_timeout_detection():

    monitor = ExecutionMonitoringEngine()

    monitor.register_transaction(
        "tx-001"
    )

    result = monitor.update_status(
        "tx-001",
        "TIMEOUT"
    )

    assert result["status"] == "TIMEOUT"


def test_monitor_history():

    monitor = ExecutionMonitoringEngine()

    monitor.register_transaction(
        "tx-001"
    )

    history = monitor.get_history()

    assert len(history) == 1


def test_missing_transaction():

    monitor = ExecutionMonitoringEngine()

    result = monitor.update_status(
        "missing",
        "FAILED"
    )

    assert result["success"] is False
