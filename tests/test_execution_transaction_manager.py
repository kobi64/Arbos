from exchanges.execution_transaction_manager import ExecutionTransactionManager


def test_create_manager():

    manager = ExecutionTransactionManager()

    assert manager is not None


def test_create_transaction():

    manager = ExecutionTransactionManager()

    tx = manager.create_transaction(
        trade_id="ARB-001"
    )

    assert tx["trade_id"] == "ARB-001"


def test_transaction_has_id():

    manager = ExecutionTransactionManager()

    tx = manager.create_transaction(
        trade_id="ARB-001"
    )

    assert "transaction_id" in tx


def test_initial_status_pending():

    manager = ExecutionTransactionManager()

    tx = manager.create_transaction(
        trade_id="ARB-001"
    )

    assert tx["status"] == "PENDING"


def test_update_status():

    manager = ExecutionTransactionManager()

    tx = manager.create_transaction(
        trade_id="ARB-001"
    )

    result = manager.update_status(
        tx["transaction_id"],
        "EXECUTING"
    )

    assert result["status"] == "EXECUTING"


def test_complete_transaction():

    manager = ExecutionTransactionManager()

    tx = manager.create_transaction(
        trade_id="ARB-001"
    )

    result = manager.update_status(
        tx["transaction_id"],
        "COMPLETED"
    )

    assert result["status"] == "COMPLETED"


def test_transaction_history():

    manager = ExecutionTransactionManager()

    manager.create_transaction(
        trade_id="ARB-001"
    )

    history = manager.get_history()

    assert len(history) == 1


def test_missing_transaction():

    manager = ExecutionTransactionManager()

    result = manager.update_status(
        "missing",
        "FAILED"
    )

    assert result["success"] is False
