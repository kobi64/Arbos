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


@pytest.mark.parametrize(
    "field",
    [
        "expected_profit",
        "minimum_profit",
        "trade_size",
        "maximum_exposure",
        "confidence_score",
        "minimum_confidence",
    ],
)
@pytest.mark.parametrize(
    "value",
    [
        None,
        "not-a-number",
        float("nan"),
        float("inf"),
        float("-inf"),
        True,
    ],
)
def test_invalid_numeric_risk_values_are_rejected(
    field,
    value,
):
    kwargs = {
        "expected_profit": 100.0,
        "minimum_profit": 20.0,
        "trade_size": 1000.0,
        "maximum_exposure": 5000.0,
        "confidence_score": 0.95,
        "minimum_confidence": 0.80,
        "failed_attempts": 0,
        "maximum_failed_attempts": 3,
    }
    kwargs[field] = value

    with pytest.raises(ValueError):
        RiskGateValidation.validate(**kwargs)


@pytest.mark.parametrize(
    "field",
    [
        "failed_attempts",
        "maximum_failed_attempts",
    ],
)
@pytest.mark.parametrize(
    "value",
    [
        None,
        "not-a-number",
        -1,
        1.5,
        "1.5",
        True,
        float("nan"),
        float("inf"),
        float("-inf"),
    ],
)
def test_invalid_failure_count_contract(
    field,
    value,
):
    kwargs = {
        "expected_profit": 100.0,
        "minimum_profit": 20.0,
        "trade_size": 1000.0,
        "maximum_exposure": 5000.0,
        "confidence_score": 0.95,
        "minimum_confidence": 0.80,
        "failed_attempts": 0,
        "maximum_failed_attempts": 3,
    }
    kwargs[field] = value

    with pytest.raises(
        ValueError,
        match="failed attempt counts must be non-negative integers",
    ):
        RiskGateValidation.validate(**kwargs)
