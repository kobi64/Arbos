import pytest

from core.fresh_repeat_scale_revalidation import (
    FreshRepeatScaleRevalidation,
)
from exchanges.network_registry import NetworkInfo


def decision(
    action="REPEAT_SAME_SIZE",
    next_trade_size=250.0,
):
    return {
        "decision": action,
        "allowed": True,
        "reason": "test_decision",
        "route_id": "ROUTE-001",
        "approval_id": "ARB-001",
        "permission_id": "PERM-001",
        "current_trade_size": 250.0,
        "next_trade_size": next_trade_size,
        "fresh_revalidation_required": True,
        "fresh_approval_required": True,
        "fresh_execution_permission_required": True,
        "test_trade": True,
        "simulated": True,
        "live_order_submitted": False,
    }


def source_networks():
    return [
        NetworkInfo(
            "USDT",
            "TRC20",
            withdraw_fee=1.0,
            min_withdraw=10.0,
        ),
        NetworkInfo(
            "USDT",
            "ERC20",
            withdraw_fee=8.0,
            min_withdraw=10.0,
        ),
    ]


def destination_networks():
    return [
        NetworkInfo(
            "USDT",
            "TRC20",
        ),
        NetworkInfo(
            "USDT",
            "ERC20",
        ),
    ]


def run_revalidation(
    decision_result=None,
    source=None,
    destination=None,
    transfer_amount=250.0,
    available_liquidity=10000.0,
    minimum_liquidity_ratio=0.1,
    expected_price=100.0,
    current_price=99.5,
    max_slippage_percent=1.0,
):
    gate = FreshRepeatScaleRevalidation()

    return gate.revalidate(
        decision_result=(
            decision()
            if decision_result is None
            else decision_result
        ),
        source_networks=(
            source_networks()
            if source is None
            else source
        ),
        destination_networks=(
            destination_networks()
            if destination is None
            else destination
        ),
        transfer_amount=transfer_amount,
        available_liquidity=available_liquidity,
        minimum_liquidity_ratio=(
            minimum_liquidity_ratio
        ),
        expected_price=expected_price,
        current_price=current_price,
        max_slippage_percent=(
            max_slippage_percent
        ),
    )


def test_repeat_same_size_can_be_revalidated():
    result = run_revalidation()

    assert result["revalidated"] is True
    assert result["allowed"] is True
    assert result["status"] == "REVALIDATED"
    assert result["decision"] == "REPEAT_SAME_SIZE"


def test_scale_up_can_be_revalidated():
    result = run_revalidation(
        decision_result=decision(
            action="SCALE_UP",
            next_trade_size=500.0,
        ),
    )

    assert result["revalidated"] is True
    assert result["decision"] == "SCALE_UP"
    assert result["next_trade_size"] == 500.0


def test_lowest_fee_shared_network_is_selected():
    result = run_revalidation()

    assert result["network"] == "TRC20"
    assert result["withdraw_fee"] == 1.0


def test_transfer_net_amount_is_recorded():
    result = run_revalidation(
        transfer_amount=250.0
    )

    assert result["transfer_net_amount"] == 249.0


def test_route_without_shared_network_is_blocked():
    destination = [
        NetworkInfo(
            "USDT",
            "BEP20",
        ),
    ]

    result = run_revalidation(
        destination=destination
    )

    assert result["revalidated"] is False
    assert result["status"] == "BLOCKED"
    assert result["reason"] == "route_not_executable"


def test_transfer_below_minimum_is_blocked():
    result = run_revalidation(
        transfer_amount=5.0
    )

    assert result["revalidated"] is False
    assert result["reason"] == "transfer_not_feasible"
    assert (
        result["transfer_reason"]
        == "below_minimum_withdrawal"
    )


def test_network_maintenance_blocks_route():
    source = [
        NetworkInfo(
            "USDT",
            "TRC20",
            withdraw_fee=1.0,
            min_withdraw=10.0,
            maintenance=True,
        ),
    ]

    result = run_revalidation(
        source=source
    )

    assert result["revalidated"] is False
    assert result["reason"] == "route_not_executable"


def test_insufficient_liquidity_blocks_repeat():
    result = run_revalidation(
        available_liquidity=1000.0
    )

    assert result["revalidated"] is False
    assert (
        result["reason"]
        == "liquidity_revalidation_failed"
    )
    assert (
        result["liquidity_reason"]
        == "insufficient_liquidity"
    )


def test_scaled_size_uses_new_size_for_liquidity():
    result = run_revalidation(
        decision_result=decision(
            action="SCALE_UP",
            next_trade_size=2000.0,
        ),
        available_liquidity=10000.0,
    )

    assert result["revalidated"] is False
    assert (
        result["reason"]
        == "liquidity_revalidation_failed"
    )


def test_excessive_slippage_blocks_repeat():
    result = run_revalidation(
        expected_price=100.0,
        current_price=98.0,
        max_slippage_percent=1.0,
    )

    assert result["revalidated"] is False
    assert (
        result["reason"]
        == "slippage_revalidation_failed"
    )
    assert (
        result["slippage_reason"]
        == "slippage_exceeded"
    )


def test_price_improvement_is_accepted():
    result = run_revalidation(
        expected_price=100.0,
        current_price=101.0,
        max_slippage_percent=1.0,
    )

    assert result["revalidated"] is True


def test_disallowed_decision_is_blocked():
    record = decision()
    record["allowed"] = False

    result = run_revalidation(
        decision_result=record
    )

    assert result["revalidated"] is False
    assert result["reason"] == "allowed_decision_required"


def test_stop_decision_is_blocked():
    record = decision(
        action="STOP"
    )

    result = run_revalidation(
        decision_result=record
    )

    assert result["revalidated"] is False
    assert (
        result["reason"]
        == "repeat_or_scale_decision_required"
    )


def test_fresh_revalidation_flag_is_required():
    record = decision()
    record["fresh_revalidation_required"] = False

    result = run_revalidation(
        decision_result=record
    )

    assert result["revalidated"] is False
    assert (
        result["reason"]
        == "fresh_revalidation_not_required"
    )


def test_live_submission_is_blocked():
    record = decision()
    record["live_order_submitted"] = True

    result = run_revalidation(
        decision_result=record
    )

    assert result["revalidated"] is False
    assert result["reason"] == "live_order_already_submitted"
    assert result["live_order_submitted"] is True


def test_invalid_next_trade_size_is_blocked():
    record = decision(
        next_trade_size=0.0
    )

    result = run_revalidation(
        decision_result=record
    )

    assert result["revalidated"] is False
    assert result["reason"] == "invalid_next_trade_size"


def test_fresh_approval_still_required_after_revalidation():
    result = run_revalidation()

    assert result["fresh_approval_required"] is True
    assert result["approval_granted"] is False


def test_fresh_permission_still_required_after_revalidation():
    result = run_revalidation()

    assert (
        result["fresh_execution_permission_required"]
        is True
    )
    assert result["permission_granted"] is False


def test_previous_control_ids_are_audit_only():
    result = run_revalidation()

    assert result["previous_approval_id"] == "ARB-001"
    assert result["previous_permission_id"] == "PERM-001"
    assert result["approval_granted"] is False
    assert result["permission_granted"] is False


def test_missing_decision_is_rejected():
    gate = FreshRepeatScaleRevalidation()

    with pytest.raises(
        ValueError,
        match="decision_result is required",
    ):
        gate.revalidate(
            decision_result=None,
            source_networks=source_networks(),
            destination_networks=(
                destination_networks()
            ),
            transfer_amount=250.0,
            available_liquidity=10000.0,
            minimum_liquidity_ratio=0.1,
            expected_price=100.0,
            current_price=99.5,
            max_slippage_percent=1.0,
        )


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
def test_invalid_next_trade_size_contract(next_trade_size):
    record = decision(
        next_trade_size=next_trade_size
    )

    result = run_revalidation(
        decision_result=record
    )

    assert result["revalidated"] is False
    assert result["allowed"] is False
    assert result["reason"] == "invalid_next_trade_size"


@pytest.mark.parametrize(
    "transfer_amount",
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
def test_invalid_transfer_amount_fails_closed(
    transfer_amount,
):
    result = run_revalidation(
        transfer_amount=transfer_amount
    )

    assert result["revalidated"] is False
    assert result["allowed"] is False
    assert result["reason"] == "invalid_transfer_amount"


@pytest.mark.parametrize(
    "field,value",
    [
        ("available_liquidity", None),
        ("available_liquidity", "bad"),
        ("available_liquidity", float("nan")),
        ("available_liquidity", float("inf")),
        ("available_liquidity", float("-inf")),
        ("available_liquidity", True),
        ("minimum_liquidity_ratio", None),
        ("minimum_liquidity_ratio", "bad"),
        ("minimum_liquidity_ratio", float("nan")),
        ("minimum_liquidity_ratio", float("inf")),
        ("minimum_liquidity_ratio", float("-inf")),
        ("minimum_liquidity_ratio", True),
        ("expected_price", None),
        ("expected_price", "bad"),
        ("expected_price", float("nan")),
        ("expected_price", float("inf")),
        ("expected_price", float("-inf")),
        ("expected_price", True),
        ("current_price", None),
        ("current_price", "bad"),
        ("current_price", float("nan")),
        ("current_price", float("inf")),
        ("current_price", float("-inf")),
        ("current_price", True),
        ("max_slippage_percent", None),
        ("max_slippage_percent", "bad"),
        ("max_slippage_percent", float("nan")),
        ("max_slippage_percent", float("inf")),
        ("max_slippage_percent", float("-inf")),
        ("max_slippage_percent", True),
    ],
)
def test_invalid_market_revalidation_inputs_fail_closed(
    field,
    value,
):
    kwargs = {
        "available_liquidity": 10000.0,
        "minimum_liquidity_ratio": 0.1,
        "expected_price": 100.0,
        "current_price": 99.5,
        "max_slippage_percent": 1.0,
    }
    kwargs[field] = value

    result = run_revalidation(**kwargs)

    assert result["revalidated"] is False
    assert result["allowed"] is False
    assert result["reason"] == "invalid_revalidation_input"


def test_numeric_string_revalidation_inputs_remain_supported():
    record = decision(
        next_trade_size="250"
    )

    result = run_revalidation(
        decision_result=record,
        transfer_amount="250",
        available_liquidity="10000",
        minimum_liquidity_ratio="0.1",
        expected_price="100",
        current_price="99.5",
        max_slippage_percent="1",
    )

    assert result["revalidated"] is True
    assert result["allowed"] is True
    assert result["next_trade_size"] == 250.0


def test_numeric_string_revalidation_contract_remains_supported():
    result = run_revalidation(
        decision_result=decision(
            next_trade_size="250.0",
        ),
        transfer_amount="250.0",
        available_liquidity="10000.0",
        minimum_liquidity_ratio="0.1",
        expected_price="100.0",
        current_price="99.5",
        max_slippage_percent="1.0",
    )

    assert result["revalidated"] is True
    assert result["allowed"] is True
    assert result["next_trade_size"] == 250.0


# EX-340 — fresh revalidation identity continuity audit


@pytest.mark.parametrize(
    "field",
    [
        "route_id",
        "approval_id",
        "permission_id",
    ],
)
@pytest.mark.parametrize(
    "value",
    [
        None,
        "",
        "   ",
        0,
        False,
    ],
)
def test_invalid_decision_control_identity_blocks_revalidation(
    field,
    value,
):
    record = decision()
    record[field] = value

    result = run_revalidation(
        decision_result=record
    )

    assert result["revalidated"] is False
    assert result["allowed"] is False
    assert result["status"] == "BLOCKED"
    assert (
        result["reason"]
        == "invalid_decision_identity"
    )
    assert result["live_order_submitted"] is False


def test_revalidation_normalizes_control_identity():
    record = decision()
    record["route_id"] = "  ROUTE-001  "
    record["approval_id"] = "  ARB-001  "
    record["permission_id"] = "  PERM-001  "

    result = run_revalidation(
        decision_result=record
    )

    assert result["revalidated"] is True
    assert result["allowed"] is True
    assert result["route_id"] == "ROUTE-001"
    assert (
        result["previous_approval_id"]
        == "ARB-001"
    )
    assert (
        result["previous_permission_id"]
        == "PERM-001"
    )


def test_revalidation_identity_normalization_does_not_mutate_decision():
    record = decision()
    record["route_id"] = "  ROUTE-001  "
    record["approval_id"] = "  ARB-001  "
    record["permission_id"] = "  PERM-001  "

    run_revalidation(
        decision_result=record
    )

    assert record["route_id"] == "  ROUTE-001  "
    assert record["approval_id"] == "  ARB-001  "
    assert record["permission_id"] == "  PERM-001  "


def test_normalized_identity_preserves_repeat_revalidation_contract():
    record = decision()
    record["route_id"] = " ROUTE-001 "
    record["approval_id"] = " ARB-001 "
    record["permission_id"] = " PERM-001 "

    result = run_revalidation(
        decision_result=record
    )

    assert result["revalidated"] is True
    assert result["allowed"] is True
    assert result["status"] == "REVALIDATED"
    assert result["decision"] == "REPEAT_SAME_SIZE"
    assert result["next_trade_size"] == 250.0
    assert result["fresh_approval_required"] is True
    assert result["approval_granted"] is False
    assert (
        result["fresh_execution_permission_required"]
        is True
    )
    assert result["permission_granted"] is False


def test_normalized_identity_preserves_scale_revalidation_contract():
    record = decision(
        action="SCALE_UP",
        next_trade_size=500.0,
    )
    record["route_id"] = " ROUTE-001 "
    record["approval_id"] = " ARB-001 "
    record["permission_id"] = " PERM-001 "

    result = run_revalidation(
        decision_result=record
    )

    assert result["revalidated"] is True
    assert result["allowed"] is True
    assert result["decision"] == "SCALE_UP"
    assert result["route_id"] == "ROUTE-001"
    assert result["next_trade_size"] == 500.0
    assert (
        result["previous_approval_id"]
        == "ARB-001"
    )
    assert (
        result["previous_permission_id"]
        == "PERM-001"
    )
