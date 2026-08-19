"""
ArbOS™

EX-351
Fresh Market Provenance Authorization Binding

Verifies that the market provenance identity produced by fresh
revalidation survives the approval boundary and that permission
handoff fails closed when the approved provenance identity differs
from the provenance identity presented for authorization.
"""

import copy

from core.repeat_scale_market_provenance_binding import (
    RepeatScaleMarketProvenanceBinding,
)


def provenance():
    return {
        "route_id": "ROUTE-001",
        "independent_revalidation_capture": True,
        "snapshot_age_verified": False,
        "snapshot_count": 2,
        "symbols": [
            "BTC/USDT",
            "BTC/USDT",
        ],
        "exchange_ids": [
            "kucoin",
            "gate",
        ],
        "earliest_timestamp": 1000.0,
        "latest_timestamp": 1000.1,
        "snapshot_spread_ms": 100.0,
        "entry_symbol": "BTC/USDT",
        "entry_side": "buy",
        "available_liquidity": 50000.0,
        "best_price": 100.0,
        "average_price": 100.2,
        "slippage_percent": 0.2,
    }


def test_exact_market_provenance_identity_verifies():
    item = provenance()

    binding = (
        RepeatScaleMarketProvenanceBinding
        .create(item)
    )

    assert (
        RepeatScaleMarketProvenanceBinding
        .verify(
            item,
            binding["market_provenance_id"],
        )
        is True
    )


def test_changed_market_state_changes_authorization_identity():
    original = provenance()

    first = (
        RepeatScaleMarketProvenanceBinding
        .create(original)[
            "market_provenance_id"
        ]
    )

    changed = copy.deepcopy(original)
    changed["average_price"] = 101.0

    second = (
        RepeatScaleMarketProvenanceBinding
        .create(changed)[
            "market_provenance_id"
        ]
    )

    assert first != second


def test_changed_liquidity_changes_authorization_identity():
    original = provenance()

    first = (
        RepeatScaleMarketProvenanceBinding
        .create(original)[
            "market_provenance_id"
        ]
    )

    changed = copy.deepcopy(original)
    changed["available_liquidity"] = 1.0

    second = (
        RepeatScaleMarketProvenanceBinding
        .create(changed)[
            "market_provenance_id"
        ]
    )

    assert first != second


def test_changed_venue_changes_authorization_identity():
    original = provenance()

    first = (
        RepeatScaleMarketProvenanceBinding
        .create(original)[
            "market_provenance_id"
        ]
    )

    changed = copy.deepcopy(original)
    changed["exchange_ids"][1] = "bitget"

    second = (
        RepeatScaleMarketProvenanceBinding
        .create(changed)[
            "market_provenance_id"
        ]
    )

    assert first != second


def test_changed_route_changes_authorization_identity():
    original = provenance()

    first = (
        RepeatScaleMarketProvenanceBinding
        .create(original)[
            "market_provenance_id"
        ]
    )

    changed = copy.deepcopy(original)
    changed["route_id"] = "ROUTE-OTHER"

    second = (
        RepeatScaleMarketProvenanceBinding
        .create(changed)[
            "market_provenance_id"
        ]
    )

    assert first != second


from core.revalidated_repeat_scale_approval_handoff import (
    RevalidatedRepeatScaleApprovalHandoff,
)


def revalidation_result_with_binding():
    item = provenance()
    binding = (
        RepeatScaleMarketProvenanceBinding
        .create(item)
    )

    return {
        "revalidated": True,
        "allowed": True,
        "status": "REVALIDATED",
        "decision": "REPEAT_SAME_SIZE",
        "route_id": "ROUTE-001",
        "previous_approval_id": "APP-OLD",
        "previous_permission_id": "PERM-OLD",
        "next_trade_size": 100.0,
        "network": "ERC20",
        "withdraw_fee": 1.0,
        "transfer_net_amount": 99.0,
        "fresh_approval_required": True,
        "fresh_execution_permission_required": True,
        "approval_granted": False,
        "permission_granted": False,
        "market_provenance_binding": binding,
        "test_trade": True,
        "simulated": True,
        "live_order_submitted": False,
    }


def prepare_approval(result):
    return (
        RevalidatedRepeatScaleApprovalHandoff()
        .prepare(
            revalidation_result=result,
            asset="BTC",
            buy_exchange="kucoin",
            sell_exchange="gate",
            expected_profit=5.0,
            estimated_fees=1.0,
            slippage_allowance=0.5,
        )
    )


def test_approval_handoff_preserves_market_provenance_identity():
    result = (
        revalidation_result_with_binding()
    )

    prepared = prepare_approval(result)

    expected = result[
        "market_provenance_binding"
    ]

    assert prepared["prepared"] is True
    assert prepared["approval_ready"] is True

    assert (
        prepared["market_provenance_id"]
        == expected["market_provenance_id"]
    )

    assert (
        prepared["approval_request"][
            "market_provenance_id"
        ]
        == expected["market_provenance_id"]
    )

    assert (
        prepared["approval_request"][
            "market_provenance_binding"
        ]
        == expected[
            "market_provenance_binding"
        ]
    )


def test_approval_handoff_rejects_missing_market_provenance_binding():
    result = (
        revalidation_result_with_binding()
    )
    result["market_provenance_binding"] = None

    prepared = prepare_approval(result)

    assert prepared["prepared"] is False
    assert prepared["approval_ready"] is False
    assert prepared["reason"] == (
        "market_provenance_binding_required"
    )
    assert (
        prepared["live_order_submitted"]
        is False
    )


def test_approval_handoff_rejects_mutated_market_provenance():
    result = (
        revalidation_result_with_binding()
    )

    result[
        "market_provenance_binding"
    ][
        "market_provenance_binding"
    ][
        "average_price"
    ] = 999.0

    prepared = prepare_approval(result)

    assert prepared["prepared"] is False
    assert prepared["approval_ready"] is False
    assert prepared["reason"] == (
        "market_provenance_binding_mismatch"
    )
    assert (
        prepared["live_order_submitted"]
        is False
    )


from core.fresh_repeat_scale_execution_permission_handoff import (
    FreshRepeatScaleExecutionPermissionHandoff,
)


def approved_result_for(prepared):
    return {
        "approval_id": "APP-FRESH",
        "route_id": prepared["route_id"],
        "approved": True,
        "status": "approved",
        "market_provenance_id": (
            prepared["market_provenance_id"]
        ),
        "trade_summary": {
            "asset": (
                prepared["approval_request"][
                    "asset"
                ]
            ),
            "trade_amount": (
                prepared["approval_request"][
                    "trade_amount"
                ]
            ),
            "route": "kucoin -> gate",
            "buy_exchange": "kucoin",
            "sell_exchange": "gate",
            "expected_profit": (
                prepared["approval_request"][
                    "expected_profit"
                ]
            ),
        },
        "live_order_submitted": False,
    }


def test_permission_handoff_preserves_approved_market_provenance():
    prepared = prepare_approval(
        revalidation_result_with_binding()
    )

    approval = approved_result_for(
        prepared
    )

    permission = (
        FreshRepeatScaleExecutionPermissionHandoff()
        .prepare(
            approval_handoff=prepared,
            approval_result=approval,
        )
    )

    assert permission["handoff_ready"] is True
    assert (
        permission["market_provenance_id"]
        == prepared["market_provenance_id"]
    )
    assert permission["permission_granted"] is False
    assert (
        permission["live_order_submitted"]
        is False
    )


def test_permission_handoff_rejects_missing_approved_market_provenance():
    prepared = prepare_approval(
        revalidation_result_with_binding()
    )

    approval = approved_result_for(
        prepared
    )
    approval.pop(
        "market_provenance_id"
    )

    permission = (
        FreshRepeatScaleExecutionPermissionHandoff()
        .prepare(
            approval_handoff=prepared,
            approval_result=approval,
        )
    )

    assert permission["handoff_ready"] is False
    assert permission["reason"] == (
        "approved_market_provenance_id_required"
    )
    assert (
        permission["live_order_submitted"]
        is False
    )


def test_permission_handoff_rejects_different_market_provenance():
    prepared = prepare_approval(
        revalidation_result_with_binding()
    )

    approval = approved_result_for(
        prepared
    )
    approval["market_provenance_id"] = (
        "different-market-state"
    )

    permission = (
        FreshRepeatScaleExecutionPermissionHandoff()
        .prepare(
            approval_handoff=prepared,
            approval_result=approval,
        )
    )

    assert permission["handoff_ready"] is False
    assert permission["reason"] == (
        "approved_market_provenance_id_mismatch"
    )
    assert (
        permission["live_order_submitted"]
        is False
    )


def test_permission_handoff_rejects_blank_bound_market_provenance():
    prepared = prepare_approval(
        revalidation_result_with_binding()
    )

    approval = approved_result_for(
        prepared
    )
    prepared["market_provenance_id"] = "   "

    permission = (
        FreshRepeatScaleExecutionPermissionHandoff()
        .prepare(
            approval_handoff=prepared,
            approval_result=approval,
        )
    )

    assert permission["handoff_ready"] is False
    assert permission["reason"] == (
        "market_provenance_id_required"
    )
    assert (
        permission["live_order_submitted"]
        is False
    )
