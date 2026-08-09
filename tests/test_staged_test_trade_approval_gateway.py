import pytest

from core.staged_test_trade_approval_gateway import (
    StagedTestTradeApprovalGateway,
)


def prepared_package():
    return {
        "prepared": True,
        "reason": "test_trade_package_prepared",
        "route_id": "DIRECT-ETH",
        "route_type": "direct_cross_exchange",
        "test_trade_amount": 250.0,
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


def test_creates_pending_manual_approval_request():
    gateway = StagedTestTradeApprovalGateway()

    result = gateway.request(
        staged_package=prepared_package(),
    )

    assert result["approval_id"].startswith("ARB-")
    assert result["approved"] is False
    assert result["status"] == "awaiting_approval"
    assert result["route_id"] == "DIRECT-ETH"
    assert result["live_order_submitted"] is False


def test_approval_request_preserves_test_trade_amount():
    gateway = StagedTestTradeApprovalGateway()

    result = gateway.request(
        staged_package=prepared_package(),
    )

    assert (
        result["trade_summary"]["trade_amount"]
        == 250.0
    )


def test_explicit_approval_grants_only_pending_request():
    gateway = StagedTestTradeApprovalGateway()

    request = gateway.request(
        staged_package=prepared_package(),
    )

    result = gateway.approve(
        approval_id=request["approval_id"],
    )

    assert result["approved"] is True
    assert result["status"] == "approved"
    assert result["live_order_submitted"] is False


def test_rejection_blocks_staged_trade():
    gateway = StagedTestTradeApprovalGateway()

    request = gateway.request(
        staged_package=prepared_package(),
    )

    result = gateway.reject(
        approval_id=request["approval_id"],
        reason="manual_rejection",
    )

    assert result["approved"] is False
    assert result["status"] == "rejected"
    assert result["reason"] == "manual_rejection"
    assert result["live_order_submitted"] is False


def test_unprepared_package_cannot_request_approval():
    gateway = StagedTestTradeApprovalGateway()

    package = prepared_package()
    package["prepared"] = False

    result = gateway.request(
        staged_package=package,
    )

    assert result["approved"] is False
    assert result["status"] == "blocked"
    assert result["reason"] == "test_trade_package_not_prepared"
    assert result["live_order_submitted"] is False


def test_package_that_already_submitted_live_order_is_blocked():
    gateway = StagedTestTradeApprovalGateway()

    package = prepared_package()
    package["live_order_submitted"] = True

    result = gateway.request(
        staged_package=package,
    )

    assert result["approved"] is False
    assert result["status"] == "blocked"
    assert result["reason"] == "live_order_already_submitted"


def test_unknown_approval_id_is_not_approved():
    gateway = StagedTestTradeApprovalGateway()

    result = gateway.approve(
        approval_id="UNKNOWN",
    )

    assert result["approved"] is False
    assert result["status"] == "not_found"
    assert result["live_order_submitted"] is False


def test_missing_package_is_rejected():
    gateway = StagedTestTradeApprovalGateway()

    with pytest.raises(
        ValueError,
        match="staged_package is required",
    ):
        gateway.request(
            staged_package=None,
        )


def test_rejected_request_cannot_later_be_approved():
    gateway = StagedTestTradeApprovalGateway()

    request = gateway.request(
        staged_package=prepared_package(),
    )

    rejected = gateway.reject(
        approval_id=request["approval_id"],
        reason="manual_rejection",
    )

    assert rejected["approved"] is False

    result = gateway.approve(
        approval_id=request["approval_id"],
    )

    assert result["approved"] is False
    assert result["status"] == "not_found"
    assert result["live_order_submitted"] is False
