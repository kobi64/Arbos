import pytest

from core.live_market_paper_session_readiness import (
    LiveMarketPaperSessionReadiness,
)


def verification_result():
    return {
        "paper_only": True,
        "live_order_submitted": False,
    }


def evaluate(**overrides):
    values = {
        "verification_result": verification_result(),
        "exchange_connected": True,
        "market_data_available": True,
        "market_data_fresh": True,
        "paper_engine_ready": True,
        "risk_controls_ready": True,
        "audit_ready": True,
        "session_enabled": True,
    }

    values.update(overrides)

    return LiveMarketPaperSessionReadiness().evaluate(
        **values
    )


def test_ready_session_passes():
    result = evaluate()

    assert result["session_ready"] is True
    assert (
        result["reason"]
        == "live_market_paper_session_ready"
    )


def test_ready_session_is_explicitly_paper_only():
    result = evaluate()

    assert result["mode"] == "PAPER"
    assert result["real_market_data"] is True
    assert result["simulated_execution"] is True
    assert result["paper_only"] is True
    assert result["live_execution_enabled"] is False
    assert result["live_order_submitted"] is False


def test_non_paper_verification_is_blocked():
    verification = verification_result()
    verification["paper_only"] = False

    result = evaluate(
        verification_result=verification
    )

    assert result["session_ready"] is False
    assert (
        result["reason"]
        == "paper_verification_required"
    )


def test_previous_live_submission_is_blocked():
    verification = verification_result()
    verification["live_order_submitted"] = True

    result = evaluate(
        verification_result=verification
    )

    assert result["session_ready"] is False
    assert (
        result["reason"]
        == "live_order_already_submitted"
    )


def test_disabled_session_is_blocked():
    result = evaluate(
        session_enabled=False
    )

    assert result["session_ready"] is False
    assert result["reason"] == "paper_session_disabled"


def test_exchange_connection_is_required():
    result = evaluate(
        exchange_connected=False
    )

    assert result["session_ready"] is False
    assert (
        result["reason"]
        == "exchange_not_connected"
    )


def test_market_data_must_be_available():
    result = evaluate(
        market_data_available=False
    )

    assert result["session_ready"] is False
    assert (
        result["reason"]
        == "market_data_unavailable"
    )


def test_market_data_must_be_fresh():
    result = evaluate(
        market_data_fresh=False
    )

    assert result["session_ready"] is False
    assert result["reason"] == "stale_market_data"


def test_paper_engine_must_be_ready():
    result = evaluate(
        paper_engine_ready=False
    )

    assert result["session_ready"] is False
    assert (
        result["reason"]
        == "paper_engine_not_ready"
    )


def test_risk_controls_must_be_ready():
    result = evaluate(
        risk_controls_ready=False
    )

    assert result["session_ready"] is False
    assert (
        result["reason"]
        == "risk_controls_not_ready"
    )


def test_audit_must_be_ready():
    result = evaluate(
        audit_ready=False
    )

    assert result["session_ready"] is False
    assert result["reason"] == "audit_not_ready"


def test_missing_verification_result_is_rejected():
    with pytest.raises(
        ValueError,
        match="verification_result is required",
    ):
        LiveMarketPaperSessionReadiness().evaluate(
            verification_result=None,
            exchange_connected=True,
            market_data_available=True,
            market_data_fresh=True,
            paper_engine_ready=True,
            risk_controls_ready=True,
            audit_ready=True,
            session_enabled=True,
        )


@pytest.mark.parametrize(
    "field",
    [
        "exchange_connected",
        "market_data_available",
        "market_data_fresh",
        "paper_engine_ready",
        "risk_controls_ready",
        "audit_ready",
        "session_enabled",
    ],
)
def test_boolean_inputs_must_be_boolean(field):
    kwargs = {
        "verification_result": (
            verification_result()
        ),
        "exchange_connected": True,
        "market_data_available": True,
        "market_data_fresh": True,
        "paper_engine_ready": True,
        "risk_controls_ready": True,
        "audit_ready": True,
        "session_enabled": True,
    }

    kwargs[field] = "yes"

    with pytest.raises(
        ValueError,
        match=f"{field} must be boolean",
    ):
        LiveMarketPaperSessionReadiness().evaluate(
            **kwargs
        )


def test_history_records_ready_result():
    gate = LiveMarketPaperSessionReadiness()

    gate.evaluate(
        verification_result=verification_result(),
        exchange_connected=True,
        market_data_available=True,
        market_data_fresh=True,
        paper_engine_ready=True,
        risk_controls_ready=True,
        audit_ready=True,
        session_enabled=True,
    )

    assert len(gate.history()) == 1
    assert gate.history()[0]["session_ready"] is True


def test_history_records_blocked_result():
    gate = LiveMarketPaperSessionReadiness()

    gate.evaluate(
        verification_result=verification_result(),
        exchange_connected=True,
        market_data_available=False,
        market_data_fresh=True,
        paper_engine_ready=True,
        risk_controls_ready=True,
        audit_ready=True,
        session_enabled=True,
    )

    assert len(gate.history()) == 1
    assert gate.history()[0]["session_ready"] is False
