import pytest

from core.approved_test_trade_handoff import (
    ApprovedTestTradeHandoff,
)


def approved_request():
    return {
        "approval_id": "ARB-001",
        "approved": True,
        "status": "approved",
        "trade_summary": {
            "asset": "ETH",
            "trade_amount": 250.0,
            "route": "kucoin -> gate",
            "expected_profit": 2.50,
            "net_profit": 1.75,
        },
        "live_order_submitted": False,
    }


def staged_package():
    return {
        "prepared": True,
        "reason": "test_trade_package_prepared",
        "route_id": "DIRECT-ETH",
        "route_type": "direct_cross_exchange",
        "test_trade_amount": 250.0,
        "maximum_trade_amount": 1000.0,
        "trade_package": {
            "ready": True,
            "trade": {
                "asset": "ETH",
                "buy_exchange": "kucoin",
                "sell_exchange": "gate",
                "trade_amount": 250.0,
                "expected_profit": 2.50,
                "estimated_fees": 0.50,
                "slippage_allowance": 0.25,
                "net_profit": 1.75,
            },
        },
        "manual_approval_required": True,
        "approval_granted": False,
        "live_order_submitted": False,
    }


def test_approved_test_trade_is_ready_for_execution_handoff():
    handoff = ApprovedTestTradeHandoff()

    result = handoff.prepare(
        staged_package=staged_package(),
        approval_result=approved_request(),
    )

    assert result["handoff_ready"] is True
    assert result["reason"] == "approved_test_trade_ready"
    assert result["route_id"] == "DIRECT-ETH"
    assert result["approval_id"] == "ARB-001"
    assert result["trade_amount"] == 250.0
    assert result["live_order_submitted"] is False


def test_unapproved_request_is_blocked():
    handoff = ApprovedTestTradeHandoff()

    approval = approved_request()
    approval["approved"] = False
    approval["status"] = "awaiting_approval"

    result = handoff.prepare(
        staged_package=staged_package(),
        approval_result=approval,
    )

    assert result["handoff_ready"] is False
    assert result["reason"] == "manual_approval_required"
    assert result["live_order_submitted"] is False


def test_unprepared_package_is_blocked():
    handoff = ApprovedTestTradeHandoff()

    package = staged_package()
    package["prepared"] = False

    result = handoff.prepare(
        staged_package=package,
        approval_result=approved_request(),
    )

    assert result["handoff_ready"] is False
    assert result["reason"] == "test_trade_package_not_prepared"
    assert result["live_order_submitted"] is False


def test_trade_amount_must_match_approved_amount():
    handoff = ApprovedTestTradeHandoff()

    approval = approved_request()
    approval["trade_summary"]["trade_amount"] = 100.0

    result = handoff.prepare(
        staged_package=staged_package(),
        approval_result=approval,
    )

    assert result["handoff_ready"] is False
    assert result["reason"] == "approved_trade_amount_mismatch"
    assert result["live_order_submitted"] is False


def test_asset_must_match_approved_asset():
    handoff = ApprovedTestTradeHandoff()

    approval = approved_request()
    approval["trade_summary"]["asset"] = "BTC"

    result = handoff.prepare(
        staged_package=staged_package(),
        approval_result=approval,
    )

    assert result["handoff_ready"] is False
    assert result["reason"] == "approved_asset_mismatch"
    assert result["live_order_submitted"] is False


def test_existing_live_submission_is_blocked():
    handoff = ApprovedTestTradeHandoff()

    package = staged_package()
    package["live_order_submitted"] = True

    result = handoff.prepare(
        staged_package=package,
        approval_result=approved_request(),
    )

    assert result["handoff_ready"] is False
    assert result["reason"] == "live_order_already_submitted"
    assert result["live_order_submitted"] is True


def test_missing_staged_package_is_rejected():
    handoff = ApprovedTestTradeHandoff()

    with pytest.raises(
        ValueError,
        match="staged_package is required",
    ):
        handoff.prepare(
            staged_package=None,
            approval_result=approved_request(),
        )


def test_missing_approval_result_is_rejected():
    handoff = ApprovedTestTradeHandoff()

    with pytest.raises(
        ValueError,
        match="approval_result is required",
    ):
        handoff.prepare(
            staged_package=staged_package(),
            approval_result=None,
        )
