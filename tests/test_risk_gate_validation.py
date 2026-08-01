import pytest

from exchanges.risk_gate_validation import RiskGateValidation


def test_accepts_trade_when_all_risk_checks_pass():
    result = RiskGateValidation.validate(
        expected_profit=50.0,
        minimum_profit=20.0,
        trade_size=1000.0,
        maximum_exposure=5000.0,
        confidence_score=0.95,
        minimum_confidence=0.80,
        failed_attempts=0,
        maximum_failed_attempts=3,
    )

    assert result["valid"] is True
    assert result["reason"] is None


def test_rejects_trade_below_minimum_profit():
    result = RiskGateValidation.validate(
        expected_profit=10.0,
        minimum_profit=20.0,
        trade_size=1000.0,
        maximum_exposure=5000.0,
        confidence_score=0.95,
        minimum_confidence=0.80,
        failed_attempts=0,
        maximum_failed_attempts=3,
    )

    assert result["valid"] is False
    assert result["reason"] == "insufficient_profit"


def test_rejects_trade_above_maximum_exposure():
    result = RiskGateValidation.validate(
        expected_profit=100.0,
        minimum_profit=20.0,
        trade_size=10000.0,
        maximum_exposure=5000.0,
        confidence_score=0.95,
        minimum_confidence=0.80,
        failed_attempts=0,
        maximum_failed_attempts=3,
    )

    assert result["valid"] is False
    assert result["reason"] == "exposure_limit_exceeded"


def test_rejects_low_confidence_route():
    result = RiskGateValidation.validate(
        expected_profit=100.0,
        minimum_profit=20.0,
        trade_size=1000.0,
        maximum_exposure=5000.0,
        confidence_score=0.50,
        minimum_confidence=0.80,
        failed_attempts=0,
        maximum_failed_attempts=3,
    )

    assert result["valid"] is False
    assert result["reason"] == "low_confidence"


def test_rejects_after_too_many_failed_attempts():
    result = RiskGateValidation.validate(
        expected_profit=100.0,
        minimum_profit=20.0,
        trade_size=1000.0,
        maximum_exposure=5000.0,
        confidence_score=0.95,
        minimum_confidence=0.80,
        failed_attempts=5,
        maximum_failed_attempts=3,
    )

    assert result["valid"] is False
    assert result["reason"] == "failure_limit_exceeded"


def test_rejects_negative_values():
    with pytest.raises(ValueError):
        RiskGateValidation.validate(
            expected_profit=-1.0,
            minimum_profit=20.0,
            trade_size=1000.0,
            maximum_exposure=5000.0,
            confidence_score=0.95,
            minimum_confidence=0.80,
            failed_attempts=0,
            maximum_failed_attempts=3,
        )


def test_accepts_exact_limits():
    result = RiskGateValidation.validate(
        expected_profit=20.0,
        minimum_profit=20.0,
        trade_size=5000.0,
        maximum_exposure=5000.0,
        confidence_score=0.80,
        minimum_confidence=0.80,
        failed_attempts=3,
        maximum_failed_attempts=3,
    )

    assert result["valid"] is True


def test_rejects_invalid_confidence_range():
    with pytest.raises(ValueError):
        RiskGateValidation.validate(
            expected_profit=100.0,
            minimum_profit=20.0,
            trade_size=1000.0,
            maximum_exposure=5000.0,
            confidence_score=1.5,
            minimum_confidence=0.80,
            failed_attempts=0,
            maximum_failed_attempts=3,
        )
