import pytest

from core.controlled_test_trade_execution_adapter import (
    ControlledTestTradeExecutionAdapter,
)


def granted_permission():
    return {
        "permission_id": "PERM-001",
        "permission_granted": True,
        "status": "execution_permission_granted",
        "route_id": "DIRECT-ETH",
        "approval_id": "ARB-001",
        "asset": "ETH",
        "trade_amount": 250.0,
        "live_order_submitted": False,
    }


def test_granted_permission_is_authorised_by_controlled_manager():
    adapter = ControlledTestTradeExecutionAdapter(
        max_trade_size=300.0
    )

    result = adapter.authorise(
        permission_result=granted_permission(),
    )

    assert result["authorised"] is True
    assert result["reason"] == "execution_authorised"
    assert result["trade_amount"] == 250.0
    assert result["permission_id"] == "PERM-001"
    assert result["live_order_submitted"] is False


def test_ungranted_permission_is_blocked():
    adapter = ControlledTestTradeExecutionAdapter()

    permission = granted_permission()
    permission["permission_granted"] = False
    permission["status"] = "awaiting_execution_permission"

    result = adapter.authorise(
        permission_result=permission,
    )

    assert result["authorised"] is False
    assert result["reason"] == "execution_permission_required"
    assert result["live_order_submitted"] is False


def test_oversized_trade_is_blocked():
    adapter = ControlledTestTradeExecutionAdapter(
        max_trade_size=100.0
    )

    result = adapter.authorise(
        permission_result=granted_permission(),
    )

    assert result["authorised"] is False
    assert result["reason"] == "trade_size_limit_exceeded"
    assert result["live_order_submitted"] is False


def test_existing_live_order_is_blocked():
    adapter = ControlledTestTradeExecutionAdapter()

    permission = granted_permission()
    permission["live_order_submitted"] = True

    result = adapter.authorise(
        permission_result=permission,
    )

    assert result["authorised"] is False
    assert result["reason"] == "live_order_already_submitted"
    assert result["live_order_submitted"] is True


def test_adapter_authorisation_is_single_use():
    adapter = ControlledTestTradeExecutionAdapter()

    permission = granted_permission()

    first = adapter.authorise(
        permission_result=permission,
    )

    second = adapter.authorise(
        permission_result=permission,
    )

    assert first["authorised"] is True
    assert second["authorised"] is False
    assert second["reason"] == "duplicate_execution_blocked"
    assert second["live_order_submitted"] is False


def test_missing_permission_result_is_rejected():
    adapter = ControlledTestTradeExecutionAdapter()

    with pytest.raises(
        ValueError,
        match="permission_result is required",
    ):
        adapter.authorise(
            permission_result=None,
        )
