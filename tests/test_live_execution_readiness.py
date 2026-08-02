from exchanges.live_execution_readiness import LiveExecutionReadiness


def test_create_readiness_checker():
    checker = LiveExecutionReadiness()

    assert checker is not None


def test_default_state_not_ready():
    checker = LiveExecutionReadiness()

    result = checker.check()

    assert result["ready"] is False


def test_approval_required():
    checker = LiveExecutionReadiness()

    checker.set_simulation_passed(True)
    checker.set_risk_passed(True)
    checker.set_balance_available(True)

    result = checker.check()

    assert result["ready"] is False


def test_all_conditions_ready():
    checker = LiveExecutionReadiness()

    checker.set_simulation_passed(True)
    checker.set_risk_passed(True)
    checker.set_balance_available(True)
    checker.set_approval_granted(True)

    result = checker.check()

    assert result["ready"] is True


def test_failed_risk_blocks_execution():
    checker = LiveExecutionReadiness()

    checker.set_simulation_passed(True)
    checker.set_risk_passed(False)
    checker.set_balance_available(True)
    checker.set_approval_granted(True)

    result = checker.check()

    assert result["ready"] is False


def test_readiness_reason_available():
    checker = LiveExecutionReadiness()

    result = checker.check()

    assert "reason" in result


def test_status_history():
    checker = LiveExecutionReadiness()

    checker.check()

    history = checker.get_history()

    assert len(history) == 1


def test_manual_reset():
    checker = LiveExecutionReadiness()

    checker.set_simulation_passed(True)
    checker.reset()

    result = checker.check()

    assert result["ready"] is False
