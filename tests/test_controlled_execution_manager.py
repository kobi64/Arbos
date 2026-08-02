from exchanges.controlled_execution_manager import ControlledExecutionManager


def test_create_manager():
    manager = ControlledExecutionManager()

    assert manager is not None


def test_default_execution_blocked():

    manager = ControlledExecutionManager()

    result = manager.execute()

    assert result["executed"] is False


def test_requires_approval():

    manager = ControlledExecutionManager()

    manager.set_trade_ready(True)

    result = manager.execute()

    assert result["executed"] is False


def test_requires_permission():

    manager = ControlledExecutionManager()

    manager.set_trade_ready(True)
    manager.set_approved(True)

    result = manager.execute()

    assert result["executed"] is False


def test_successful_execution():

    manager = ControlledExecutionManager()

    manager.set_trade_ready(True)
    manager.set_approved(True)
    manager.set_execution_permission(True)

    result = manager.execute()

    assert result["executed"] is True


def test_trade_size_limit():

    manager = ControlledExecutionManager(
        max_trade_size=1000
    )

    manager.set_trade_ready(True)
    manager.set_approved(True)
    manager.set_execution_permission(True)

    result = manager.execute(
        trade_size=5000
    )

    assert result["executed"] is False


def test_execution_history():

    manager = ControlledExecutionManager()

    manager.execute()

    history = manager.get_history()

    assert len(history) == 1


def test_duplicate_execution_blocked():

    manager = ControlledExecutionManager()

    manager.set_trade_ready(True)
    manager.set_approved(True)
    manager.set_execution_permission(True)

    first = manager.execute()

    second = manager.execute()

    assert first["executed"] is True
    assert second["executed"] is False
