import pytest

from core.revalidated_repeat_scale_approval_handoff import (
    RevalidatedRepeatScaleApprovalHandoff,
)


def revalidated_result(
    decision="REPEAT_SAME_SIZE",
    next_trade_size=250.0,
):
    return {
        "revalidated": True,
        "allowed": True,
        "status": "REVALIDATED",
        "reason": (
            "fresh_repeat_scale_revalidation_passed"
        ),
        "decision": decision,
        "route_id": "ROUTE-001",
        "previous_approval_id": "ARB-001",
        "previous_permission_id": "PERM-001",
        "next_trade_size": next_trade_size,
        "network": "TRC20",
        "withdraw_fee": 1.0,
        "transfer_net_amount": 249.0,
        "fresh_approval_required": True,
        "fresh_execution_permission_required": True,
        "approval_granted": False,
        "permission_granted": False,
        "test_trade": True,
        "simulated": True,
        "live_order_submitted": False,
    }


def prepare(
    result=None,
    asset="ETH",
    buy_exchange="kucoin",
    sell_exchange="gate",
    expected_profit=5.0,
    estimated_fees=0.5,
    slippage_allowance=0.25,
):
    handoff = (
        RevalidatedRepeatScaleApprovalHandoff()
    )

    return handoff.prepare(
        revalidation_result=(
            revalidated_result()
            if result is None
            else result
        ),
        asset=asset,
        buy_exchange=buy_exchange,
        sell_exchange=sell_exchange,
        expected_profit=expected_profit,
        estimated_fees=estimated_fees,
        slippage_allowance=slippage_allowance,
    )


def test_repeat_is_prepared_for_fresh_approval():
    result = prepare()

    assert result["prepared"] is True
    assert result["approval_ready"] is True
    assert (
        result["reason"]
        == "fresh_repeat_scale_approval_ready"
    )
    assert result["decision"] == "REPEAT_SAME_SIZE"


def test_scale_is_prepared_for_fresh_approval():
    result = prepare(
        result=revalidated_result(
            decision="SCALE_UP",
            next_trade_size=500.0,
        )
    )

    assert result["prepared"] is True
    assert result["approval_ready"] is True
    assert result["decision"] == "SCALE_UP"
    assert result["trade_amount"] == 500.0


def test_new_trade_amount_matches_revalidated_size():
    result = prepare(
        result=revalidated_result(
            next_trade_size=500.0
        )
    )

    assert result["trade_amount"] == 500.0
    assert (
        result["approval_request"]["trade_amount"]
        == 500.0
    )


def test_approval_request_contains_trade_identity():
    result = prepare()

    request = result["approval_request"]

    assert request["route_id"] == "ROUTE-001"
    assert request["asset"] == "ETH"
    assert request["buy_exchange"] == "kucoin"
    assert request["sell_exchange"] == "gate"


def test_asset_is_normalized():
    result = prepare(
        asset=" eth "
    )

    assert (
        result["approval_request"]["asset"]
        == "ETH"
    )


def test_fresh_approval_is_not_granted():
    result = prepare()

    assert result["manual_approval_required"] is True
    assert result["fresh_approval_required"] is True
    assert result["approval_granted"] is False


def test_execution_permission_is_not_granted():
    result = prepare()

    assert (
        result["fresh_execution_permission_required"]
        is True
    )
    assert result["permission_granted"] is False


def test_previous_control_ids_are_audit_only():
    result = prepare()

    assert result["previous_approval_id"] == "ARB-001"
    assert result["previous_permission_id"] == "PERM-001"
    assert result["approval_granted"] is False
    assert result["permission_granted"] is False


def test_network_revalidation_metadata_is_preserved():
    result = prepare()

    request = result["approval_request"]

    assert request["network"] == "TRC20"
    assert request["withdraw_fee"] == 1.0
    assert request["transfer_net_amount"] == 249.0


def test_profit_and_cost_inputs_are_preserved():
    result = prepare(
        expected_profit=8.0,
        estimated_fees=1.5,
        slippage_allowance=0.5,
    )

    request = result["approval_request"]

    assert request["expected_profit"] == 8.0
    assert request["estimated_fees"] == 1.5
    assert request["slippage_allowance"] == 0.5


def test_failed_revalidation_is_blocked():
    record = revalidated_result()
    record["revalidated"] = False

    result = prepare(
        result=record
    )

    assert result["prepared"] is False
    assert result["approval_ready"] is False
    assert result["reason"] == "fresh_revalidation_required"


def test_disallowed_revalidation_is_blocked():
    record = revalidated_result()
    record["allowed"] = False

    result = prepare(
        result=record
    )

    assert result["prepared"] is False
    assert (
        result["reason"]
        == "revalidated_trade_not_allowed"
    )


def test_wrong_revalidation_status_is_blocked():
    record = revalidated_result()
    record["status"] = "BLOCKED"

    result = prepare(
        result=record
    )

    assert result["prepared"] is False
    assert result["reason"] == "revalidated_status_required"


def test_fresh_approval_requirement_is_mandatory():
    record = revalidated_result()
    record["fresh_approval_required"] = False

    result = prepare(
        result=record
    )

    assert result["prepared"] is False
    assert (
        result["reason"]
        == "fresh_approval_requirement_missing"
    )


def test_existing_approval_is_rejected():
    record = revalidated_result()
    record["approval_granted"] = True

    result = prepare(
        result=record
    )

    assert result["prepared"] is False
    assert (
        result["reason"]
        == "fresh_approval_must_be_ungranted"
    )


def test_existing_permission_is_rejected():
    record = revalidated_result()
    record["permission_granted"] = True

    result = prepare(
        result=record
    )

    assert result["prepared"] is False
    assert (
        result["reason"]
        == "execution_permission_must_be_ungranted"
    )


def test_live_submission_is_blocked():
    record = revalidated_result()
    record["live_order_submitted"] = True

    result = prepare(
        result=record
    )

    assert result["prepared"] is False
    assert result["reason"] == "live_order_already_submitted"
    assert result["live_order_submitted"] is True


def test_invalid_trade_amount_is_blocked():
    record = revalidated_result(
        next_trade_size=0.0
    )

    result = prepare(
        result=record
    )

    assert result["prepared"] is False
    assert result["reason"] == "invalid_trade_amount"


def test_missing_revalidation_result_is_rejected():
    handoff = (
        RevalidatedRepeatScaleApprovalHandoff()
    )

    with pytest.raises(
        ValueError,
        match="revalidation_result is required",
    ):
        handoff.prepare(
            revalidation_result=None,
            asset="ETH",
            buy_exchange="kucoin",
            sell_exchange="gate",
            expected_profit=5.0,
            estimated_fees=0.5,
            slippage_allowance=0.25,
        )


def test_missing_asset_is_rejected():
    with pytest.raises(
        ValueError,
        match="asset is required",
    ):
        prepare(
            asset=" "
        )


def test_missing_buy_exchange_is_rejected():
    with pytest.raises(
        ValueError,
        match="buy_exchange is required",
    ):
        prepare(
            buy_exchange=""
        )


def test_missing_sell_exchange_is_rejected():
    with pytest.raises(
        ValueError,
        match="sell_exchange is required",
    ):
        prepare(
            sell_exchange=""
        )


def test_no_live_order_is_submitted():
    result = prepare()

    assert result["test_trade"] is True
    assert result["simulated"] is True
    assert result["live_order_submitted"] is False


@pytest.mark.parametrize(
    "next_trade_size",
    [
        None,
        "bad",
        float("nan"),
        float("inf"),
        float("-inf"),
        True,
    ],
)
def test_invalid_trade_amount_numeric_contract(
    next_trade_size,
):
    record = revalidated_result(
        next_trade_size=next_trade_size
    )

    result = prepare(result=record)

    assert result["prepared"] is False
    assert result["approval_ready"] is False
    assert result["reason"] == "invalid_trade_amount"


@pytest.mark.parametrize(
    "field,value",
    [
        ("expected_profit", None),
        ("expected_profit", "bad"),
        ("expected_profit", float("nan")),
        ("expected_profit", float("inf")),
        ("expected_profit", float("-inf")),
        ("expected_profit", True),
        ("estimated_fees", None),
        ("estimated_fees", "bad"),
        ("estimated_fees", float("nan")),
        ("estimated_fees", float("inf")),
        ("estimated_fees", float("-inf")),
        ("estimated_fees", True),
        ("estimated_fees", -0.01),
        ("slippage_allowance", None),
        ("slippage_allowance", "bad"),
        ("slippage_allowance", float("nan")),
        ("slippage_allowance", float("inf")),
        ("slippage_allowance", float("-inf")),
        ("slippage_allowance", True),
        ("slippage_allowance", -0.01),
    ],
)
def test_invalid_approval_economic_input_is_rejected(
    field,
    value,
):
    kwargs = {
        "expected_profit": 5.0,
        "estimated_fees": 0.5,
        "slippage_allowance": 0.25,
    }
    kwargs[field] = value

    with pytest.raises(
        ValueError,
        match=(
            f"{field} must be a finite "
            + (
                "non-negative number"
                if field in {
                    "estimated_fees",
                    "slippage_allowance",
                }
                else "number"
            )
        ),
    ):
        prepare(**kwargs)


def test_numeric_string_approval_economics_remain_supported():
    result = prepare(
        result=revalidated_result(
            next_trade_size="250",
        ),
        expected_profit="5",
        estimated_fees="0.5",
        slippage_allowance="0.25",
    )

    assert result["prepared"] is True
    assert result["approval_ready"] is True

    request = result["approval_request"]

    assert request["trade_amount"] == 250.0
    assert request["expected_profit"] == 5.0
    assert request["estimated_fees"] == 0.5
    assert request["slippage_allowance"] == 0.25


@pytest.mark.parametrize(
    "expected_profit",
    [
        0.0,
        -0.01,
        "0",
        "-1.0",
    ],
)
def test_non_positive_expected_profit_is_not_approval_ready(
    expected_profit,
):
    result = prepare(
        result=revalidated_result(
            next_trade_size=250.0,
        ),
        expected_profit=expected_profit,
        estimated_fees=0.5,
        slippage_allowance=0.25,
    )

    assert result["prepared"] is False
    assert result["approval_ready"] is False
    assert result["reason"] == "non_positive_expected_profit"
    assert result["live_order_submitted"] is False


# EX-327 — approval handoff identity audit


def test_route_identity_is_preserved_into_approval_request():
    result = prepare()

    assert result["prepared"] is True
    assert result["route_id"] == "ROUTE-001"
    assert (
        result["approval_request"]["route_id"]
        == "ROUTE-001"
    )


def test_route_identity_whitespace_is_normalized():
    record = revalidated_result()
    record["route_id"] = "  ROUTE-001  "

    result = prepare(
        result=record
    )

    assert result["prepared"] is True
    assert result["route_id"] == "ROUTE-001"
    assert (
        result["approval_request"]["route_id"]
        == "ROUTE-001"
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
def test_invalid_revalidated_route_identity_is_blocked(
    route_id,
):
    record = revalidated_result()
    record["route_id"] = route_id

    result = prepare(
        result=record
    )

    assert result["prepared"] is False
    assert result["approval_ready"] is False
    assert result["reason"] == "route_id_required"


def test_previous_control_ids_remain_lineage_only():
    result = prepare()

    assert result["previous_approval_id"] == "ARB-001"
    assert result["previous_permission_id"] == "PERM-001"
    assert result["approval_granted"] is False
    assert result["permission_granted"] is False
    assert "approval_id" not in result
    assert "permission_id" not in result
