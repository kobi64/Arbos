import pytest

from core.fresh_repeat_scale_execution_permission_handoff import (
    FreshRepeatScaleExecutionPermissionHandoff,
)
from core.staged_test_trade_execution_permission import (
    StagedTestTradeExecutionPermission,
)


def approval_handoff(
    decision="REPEAT_SAME_SIZE",
    trade_amount=250.0,
):
    return {
        "prepared": True,
        "approval_ready": True,
        "reason": (
            "fresh_repeat_scale_approval_ready"
        ),
        "route_id": "ROUTE-001",
        "decision": decision,
        "trade_amount": trade_amount,
        "approval_request": {
            "route_id": "ROUTE-001",
            "decision": decision,
            "asset": "ETH",
            "buy_exchange": "kucoin",
            "sell_exchange": "gate",
            "trade_amount": trade_amount,
            "expected_profit": 5.0,
            "estimated_fees": 0.5,
            "slippage_allowance": 0.25,
            "network": "TRC20",
        },
        "previous_approval_id": "ARB-001",
        "previous_permission_id": "PERM-001",
        "manual_approval_required": True,
        "fresh_approval_required": True,
        "approval_granted": False,
        "fresh_execution_permission_required": True,
        "permission_granted": False,
        "test_trade": True,
        "simulated": True,
        "live_order_submitted": False,
    }


def fresh_approval(
    approval_id="ARB-002",
    trade_amount=250.0,
    asset="ETH",
):
    return {
        "approval_id": approval_id,
        "route_id": "ROUTE-001",
        "approved": True,
        "status": "approved",
        "trade_summary": {
            "asset": asset,
            "trade_amount": trade_amount,
            "route": "kucoin -> gate",
            "expected_profit": 5.0,
        },
        "live_order_submitted": False,
    }


def prepare(
    handoff=None,
    approval=None,
):
    gate = (
        FreshRepeatScaleExecutionPermissionHandoff()
    )

    return gate.prepare(
        approval_handoff=(
            approval_handoff()
            if handoff is None
            else handoff
        ),
        approval_result=(
            fresh_approval()
            if approval is None
            else approval
        ),
    )


def test_fresh_approved_repeat_is_ready():
    result = prepare()

    assert result["handoff_ready"] is True
    assert (
        result["reason"]
        == "fresh_repeat_scale_permission_handoff_ready"
    )
    assert result["decision"] == "REPEAT_SAME_SIZE"


def test_fresh_approved_scale_is_ready():
    result = prepare(
        handoff=approval_handoff(
            decision="SCALE_UP",
            trade_amount=500.0,
        ),
        approval=fresh_approval(
            trade_amount=500.0,
        ),
    )

    assert result["handoff_ready"] is True
    assert result["decision"] == "SCALE_UP"
    assert result["trade_amount"] == 500.0


def test_fresh_approval_id_is_used():
    result = prepare()

    assert result["approval_id"] == "ARB-002"
    assert result["previous_approval_id"] == "ARB-001"


def test_previous_permission_is_audit_only():
    result = prepare()

    assert result["previous_permission_id"] == "PERM-001"
    assert result["permission_granted"] is False


def test_unapproved_trade_is_blocked():
    approval = fresh_approval()
    approval["approved"] = False
    approval["status"] = "awaiting_approval"

    result = prepare(
        approval=approval
    )

    assert result["handoff_ready"] is False
    assert result["reason"] == "fresh_manual_approval_required"


def test_unprepared_approval_handoff_is_blocked():
    handoff = approval_handoff()
    handoff["prepared"] = False

    result = prepare(
        handoff=handoff
    )

    assert result["handoff_ready"] is False
    assert result["reason"] == "approval_handoff_not_prepared"


def test_approval_ready_flag_is_required():
    handoff = approval_handoff()
    handoff["approval_ready"] = False

    result = prepare(
        handoff=handoff
    )

    assert result["handoff_ready"] is False
    assert result["reason"] == "fresh_approval_not_ready"


def test_fresh_approval_requirement_is_required():
    handoff = approval_handoff()
    handoff["fresh_approval_required"] = False

    result = prepare(
        handoff=handoff
    )

    assert result["handoff_ready"] is False
    assert (
        result["reason"]
        == "fresh_approval_requirement_missing"
    )


def test_fresh_permission_requirement_is_required():
    handoff = approval_handoff()
    handoff[
        "fresh_execution_permission_required"
    ] = False

    result = prepare(
        handoff=handoff
    )

    assert result["handoff_ready"] is False
    assert (
        result["reason"]
        == "fresh_execution_permission_requirement_missing"
    )


def test_trade_amount_must_match_fresh_approval():
    result = prepare(
        approval=fresh_approval(
            trade_amount=100.0
        )
    )

    assert result["handoff_ready"] is False
    assert result["reason"] == "approved_trade_amount_mismatch"


def test_asset_must_match_fresh_approval():
    result = prepare(
        approval=fresh_approval(
            asset="BTC"
        )
    )

    assert result["handoff_ready"] is False
    assert result["reason"] == "approved_asset_mismatch"


def test_route_id_must_match_when_approval_supplies_it():
    approval = fresh_approval()
    approval["route_id"] = "OTHER-ROUTE"

    result = prepare(
        approval=approval
    )

    assert result["handoff_ready"] is False
    assert result["reason"] == "approved_route_id_mismatch"


def test_fresh_approval_id_is_required():
    approval = fresh_approval()
    approval["approval_id"] = None

    result = prepare(
        approval=approval
    )

    assert result["handoff_ready"] is False
    assert result["reason"] == "fresh_approval_id_required"


def test_previous_approval_id_cannot_be_reused():
    result = prepare(
        approval=fresh_approval(
            approval_id="ARB-001"
        )
    )

    assert result["handoff_ready"] is False
    assert (
        result["reason"]
        == "previous_approval_id_reuse_blocked"
    )


def test_invalid_requested_amount_is_blocked():
    handoff = approval_handoff(
        trade_amount=0.0
    )

    result = prepare(
        handoff=handoff,
        approval=fresh_approval(
            trade_amount=0.0
        ),
    )

    assert result["handoff_ready"] is False
    assert result["reason"] == "invalid_requested_trade_amount"


def test_missing_requested_asset_is_blocked():
    handoff = approval_handoff()
    handoff["approval_request"]["asset"] = ""

    result = prepare(
        handoff=handoff
    )

    assert result["handoff_ready"] is False
    assert result["reason"] == "requested_asset_required"


def test_existing_live_submission_is_blocked():
    handoff = approval_handoff()
    handoff["live_order_submitted"] = True

    result = prepare(
        handoff=handoff
    )

    assert result["handoff_ready"] is False
    assert result["reason"] == "live_order_already_submitted"
    assert result["live_order_submitted"] is True


def test_output_can_create_new_execution_permission():
    result = prepare()

    permission_gate = (
        StagedTestTradeExecutionPermission()
    )

    permission = permission_gate.create(
        handoff_result=result
    )

    assert permission["permission_granted"] is False
    assert (
        permission["status"]
        == "awaiting_execution_permission"
    )
    assert permission["approval_id"] == "ARB-002"
    assert permission["trade_amount"] == 250.0


def test_new_permission_requires_exact_repeat_amount():
    result = prepare()

    permission_gate = (
        StagedTestTradeExecutionPermission()
    )

    permission = permission_gate.create(
        handoff_result=result
    )

    granted = permission_gate.grant(
        permission_id=permission["permission_id"],
        trade_amount=250.0,
    )

    assert granted["permission_granted"] is True
    assert granted["trade_amount"] == 250.0


def test_scaled_permission_requires_exact_scaled_amount():
    result = prepare(
        handoff=approval_handoff(
            decision="SCALE_UP",
            trade_amount=500.0,
        ),
        approval=fresh_approval(
            trade_amount=500.0,
        ),
    )

    permission_gate = (
        StagedTestTradeExecutionPermission()
    )

    permission = permission_gate.create(
        handoff_result=result
    )

    wrong = permission_gate.grant(
        permission_id=permission["permission_id"],
        trade_amount=250.0,
    )

    assert wrong["permission_granted"] is False
    assert wrong["reason"] == "trade_amount_mismatch"


def test_new_permission_remains_single_use():
    result = prepare()

    permission_gate = (
        StagedTestTradeExecutionPermission()
    )

    permission = permission_gate.create(
        handoff_result=result
    )

    first = permission_gate.grant(
        permission_id=permission["permission_id"],
        trade_amount=250.0,
    )

    second = permission_gate.grant(
        permission_id=permission["permission_id"],
        trade_amount=250.0,
    )

    assert first["permission_granted"] is True
    assert second["permission_granted"] is False
    assert second["status"] == "not_found"


def test_missing_approval_handoff_is_rejected():
    gate = (
        FreshRepeatScaleExecutionPermissionHandoff()
    )

    with pytest.raises(
        ValueError,
        match="approval_handoff is required",
    ):
        gate.prepare(
            approval_handoff=None,
            approval_result=fresh_approval(),
        )


def test_missing_approval_result_is_rejected():
    gate = (
        FreshRepeatScaleExecutionPermissionHandoff()
    )

    with pytest.raises(
        ValueError,
        match="approval_result is required",
    ):
        gate.prepare(
            approval_handoff=approval_handoff(),
            approval_result=None,
        )


def test_no_live_order_is_submitted():
    result = prepare()

    assert result["test_trade"] is True
    assert result["simulated"] is True
    assert result["live_order_submitted"] is False


@pytest.mark.parametrize(
    "trade_amount",
    [
        None,
        "bad",
        float("nan"),
        float("inf"),
        float("-inf"),
        True,
        0.0,
        -1.0,
    ],
)
def test_invalid_requested_trade_amount_contract(
    trade_amount,
):
    handoff = approval_handoff(
        trade_amount=trade_amount
    )

    result = prepare(
        handoff=handoff,
        approval=fresh_approval(
            trade_amount=250.0,
        ),
    )

    assert result["handoff_ready"] is False
    assert (
        result["reason"]
        == "invalid_requested_trade_amount"
    )


@pytest.mark.parametrize(
    "trade_amount",
    [
        None,
        "bad",
        float("nan"),
        float("inf"),
        float("-inf"),
        True,
        0.0,
        -1.0,
    ],
)
def test_invalid_approved_trade_amount_contract(
    trade_amount,
):
    result = prepare(
        approval=fresh_approval(
            trade_amount=trade_amount
        )
    )

    assert result["handoff_ready"] is False
    assert (
        result["reason"]
        == "invalid_approved_trade_amount"
    )


def test_numeric_string_amounts_remain_supported():
    result = prepare(
        handoff=approval_handoff(
            trade_amount="250"
        ),
        approval=fresh_approval(
            trade_amount="250"
        ),
    )

    assert result["handoff_ready"] is True
    assert result["trade_amount"] == 250.0


@pytest.mark.parametrize(
    "approval_id",
    [
        "",
        "   ",
        0,
        False,
        [],
        {},
    ],
)
def test_fresh_approval_id_requires_non_empty_string(
    approval_id,
):
    result = prepare(
        approval=fresh_approval(
            approval_id=approval_id
        )
    )

    assert result["handoff_ready"] is False
    assert result["reason"] == "fresh_approval_id_required"


def test_whitespace_previous_approval_id_does_not_match_fresh_id():
    handoff = approval_handoff()
    handoff["previous_approval_id"] = " ARB-002 "

    result = prepare(
        handoff=handoff,
        approval=fresh_approval(
            approval_id="ARB-002"
        ),
    )

    assert result["handoff_ready"] is False
    assert (
        result["reason"]
        == "previous_approval_id_reuse_blocked"
    )


@pytest.mark.parametrize(
    "route_id",
    [
        None,
        "",
        "   ",
        0,
        False,
    ],
)
def test_requested_route_id_is_required(
    route_id,
):
    handoff = approval_handoff()
    handoff["route_id"] = route_id
    handoff["approval_request"]["route_id"] = route_id

    approval = fresh_approval()
    approval["route_id"] = route_id

    result = prepare(
        handoff=handoff,
        approval=approval,
    )

    assert result["handoff_ready"] is False
    assert result["reason"] == "route_id_required"


@pytest.mark.parametrize(
    "asset",
    [
        None,
        0,
        False,
        [],
        {},
    ],
)
def test_requested_asset_requires_real_non_empty_string(
    asset,
):
    handoff = approval_handoff()
    handoff["approval_request"]["asset"] = asset

    result = prepare(
        handoff=handoff,
    )

    assert result["handoff_ready"] is False
    assert result["reason"] == "requested_asset_required"


def test_whitespace_requested_asset_is_blocked():
    handoff = approval_handoff()
    handoff["approval_request"]["asset"] = "   "

    result = prepare(
        handoff=handoff,
    )

    assert result["handoff_ready"] is False
    assert result["reason"] == "requested_asset_required"


# EX-328 — fresh approval request identity binding


def test_requested_buy_exchange_must_match_fresh_approval():
    handoff = approval_handoff()
    handoff["approval_request"]["buy_exchange"] = "kucoin"

    approval = fresh_approval()
    approval["trade_summary"]["route"] = "gate -> gate"

    result = prepare(
        handoff=handoff,
        approval=approval,
    )

    assert result["handoff_ready"] is False
    assert result["reason"] == "approved_buy_exchange_mismatch"


def test_requested_sell_exchange_must_match_fresh_approval():
    handoff = approval_handoff()
    handoff["approval_request"]["sell_exchange"] = "gate"

    approval = fresh_approval()
    approval["trade_summary"]["route"] = "kucoin -> bitget"

    result = prepare(
        handoff=handoff,
        approval=approval,
    )

    assert result["handoff_ready"] is False
    assert result["reason"] == "approved_sell_exchange_mismatch"


def test_matching_approval_route_is_accepted():
    handoff = approval_handoff()
    handoff["approval_request"]["buy_exchange"] = "kucoin"
    handoff["approval_request"]["sell_exchange"] = "gate"

    approval = fresh_approval()
    approval["trade_summary"]["route"] = "kucoin -> gate"

    result = prepare(
        handoff=handoff,
        approval=approval,
    )

    assert result["handoff_ready"] is True


@pytest.mark.parametrize(
    "buy_exchange",
    [
        None,
        "",
        "   ",
        0,
        False,
        [],
        {},
    ],
)
def test_requested_buy_exchange_requires_real_non_empty_string(
    buy_exchange,
):
    handoff = approval_handoff()
    handoff["approval_request"]["buy_exchange"] = buy_exchange

    result = prepare(
        handoff=handoff,
    )

    assert result["handoff_ready"] is False
    assert result["reason"] == "requested_buy_exchange_required"


@pytest.mark.parametrize(
    "sell_exchange",
    [
        None,
        "",
        "   ",
        0,
        False,
        [],
        {},
    ],
)
def test_requested_sell_exchange_requires_real_non_empty_string(
    sell_exchange,
):
    handoff = approval_handoff()
    handoff["approval_request"]["sell_exchange"] = sell_exchange

    result = prepare(
        handoff=handoff,
    )

    assert result["handoff_ready"] is False
    assert result["reason"] == "requested_sell_exchange_required"


@pytest.mark.parametrize(
    "route",
    [
        None,
        "",
        "   ",
        0,
        False,
        [],
        {},
    ],
)
def test_approved_route_requires_real_non_empty_string(
    route,
):
    approval = fresh_approval()
    approval["trade_summary"]["route"] = route

    result = prepare(
        approval=approval,
    )

    assert result["handoff_ready"] is False
    assert result["reason"] == "approved_route_required"


def test_exchange_whitespace_is_normalized_for_identity_match():
    handoff = approval_handoff()
    handoff["approval_request"]["buy_exchange"] = "  kucoin  "
    handoff["approval_request"]["sell_exchange"] = "  gate  "

    approval = fresh_approval()
    approval["trade_summary"]["route"] = "  kucoin -> gate  "

    result = prepare(
        handoff=handoff,
        approval=approval,
    )

    assert result["handoff_ready"] is True


def test_successful_handoff_propagates_approved_exchange_identity():
    result = prepare()

    assert result["handoff_ready"] is True
    assert result["buy_exchange"] == "kucoin"
    assert result["sell_exchange"] == "gate"
