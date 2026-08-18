import pytest

from core.staged_execution_readiness_gate import (
    StagedExecutionReadinessGate,
)


def safe_context():
    return {
        "exchange_healthy": True,
        "market_data_fresh": True,
        "sufficient_balance": True,
        "valid_order_size": True,
        "network_supported": True,
        "reconciliation_clear": True,
    }


def profitable_scan():
    return {
        "best_profitable_route": {
            "route_id": "DIRECT-ETH",
            "route_type": "direct_cross_exchange",
            "executable": True,
            "net_final_value": 101.0,
            "net_profit": 1.0,
            "net_profit_percent": 1.0,
        },
        "paper_only": True,
        "live_order_submitted": False,
    }


def test_profitable_safe_paper_route_is_ready_for_staging():
    gate = StagedExecutionReadinessGate()

    result = gate.evaluate(
        scan_result=profitable_scan(),
        safety_context=safe_context(),
    )

    assert result["ready_for_staged_execution"] is True
    assert result["reason"] == "ready_for_staged_execution"
    assert result["route"]["route_id"] == "DIRECT-ETH"
    assert result["live_order_submitted"] is False


def test_no_profitable_route_is_not_ready():
    gate = StagedExecutionReadinessGate()

    scan = profitable_scan()
    scan["best_profitable_route"] = None

    result = gate.evaluate(
        scan_result=scan,
        safety_context=safe_context(),
    )

    assert result["ready_for_staged_execution"] is False
    assert result["reason"] == "no_profitable_route"
    assert result["route"] is None


def test_failed_execution_safety_blocks_staging():
    gate = StagedExecutionReadinessGate()

    context = safe_context()
    context["market_data_fresh"] = False

    result = gate.evaluate(
        scan_result=profitable_scan(),
        safety_context=context,
    )

    assert result["ready_for_staged_execution"] is False
    assert result["reason"] == "execution_safety_failed"
    assert "STALE_MARKET_DATA" in result["reasons"]


def test_non_paper_result_is_rejected():
    gate = StagedExecutionReadinessGate()

    scan = profitable_scan()
    scan["paper_only"] = False

    result = gate.evaluate(
        scan_result=scan,
        safety_context=safe_context(),
    )

    assert result["ready_for_staged_execution"] is False
    assert result["reason"] == "paper_verification_required"


def test_previous_live_order_submission_is_rejected():
    gate = StagedExecutionReadinessGate()

    scan = profitable_scan()
    scan["live_order_submitted"] = True

    result = gate.evaluate(
        scan_result=scan,
        safety_context=safe_context(),
    )

    assert result["ready_for_staged_execution"] is False
    assert result["reason"] == "live_order_already_submitted"


def test_missing_scan_result_is_rejected():
    gate = StagedExecutionReadinessGate()

    with pytest.raises(
        ValueError,
        match="scan_result is required",
    ):
        gate.evaluate(
            scan_result=None,
            safety_context=safe_context(),
        )


def test_non_executable_profitable_route_is_not_ready():
    scan = profitable_scan()
    scan["best_profitable_route"]["executable"] = False

    result = StagedExecutionReadinessGate().evaluate(
        scan_result=scan,
        safety_context=safe_context(),
    )

    assert result["ready_for_staged_execution"] is False
    assert result["reason"] == "route_not_executable"


@pytest.mark.parametrize(
    "executable",
    [
        None,
        0,
        1,
        "true",
        "false",
    ],
)
def test_route_executable_requires_real_true_boolean(
    executable,
):
    scan = profitable_scan()
    scan["best_profitable_route"][
        "executable"
    ] = executable

    result = StagedExecutionReadinessGate().evaluate(
        scan_result=scan,
        safety_context=safe_context(),
    )

    assert result["ready_for_staged_execution"] is False
    assert result["reason"] == "route_not_executable"


@pytest.mark.parametrize(
    "field,value",
    [
        ("net_profit", None),
        ("net_profit", "bad"),
        ("net_profit", float("nan")),
        ("net_profit", float("inf")),
        ("net_profit", float("-inf")),
        ("net_profit", True),
        ("net_profit", 0.0),
        ("net_profit", -1.0),
        ("net_profit_percent", None),
        ("net_profit_percent", "bad"),
        ("net_profit_percent", float("nan")),
        ("net_profit_percent", float("inf")),
        ("net_profit_percent", float("-inf")),
        ("net_profit_percent", True),
        ("net_profit_percent", 0.0),
        ("net_profit_percent", -1.0),
    ],
)
def test_invalid_route_profitability_is_not_ready(
    field,
    value,
):
    scan = profitable_scan()
    scan["best_profitable_route"][field] = value

    result = StagedExecutionReadinessGate().evaluate(
        scan_result=scan,
        safety_context=safe_context(),
    )

    assert result["ready_for_staged_execution"] is False
    assert result["reason"] == "invalid_route_profitability"


def test_numeric_string_route_profitability_remains_supported():
    scan = profitable_scan()
    scan["best_profitable_route"]["net_profit"] = "1.0"
    scan["best_profitable_route"][
        "net_profit_percent"
    ] = "1.0"

    result = StagedExecutionReadinessGate().evaluate(
        scan_result=scan,
        safety_context=safe_context(),
    )

    assert result["ready_for_staged_execution"] is True
    assert result["reason"] == "ready_for_staged_execution"
