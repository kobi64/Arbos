import pytest

from core.end_to_end_live_market_paper_cycle_controller import (
    EndToEndLiveMarketPaperCycleController,
)
from exchanges.network_registry import NetworkInfo


class FakeSnapshotEngine:
    def __init__(self):
        self.timestamp = 1000

    def snapshot(
        self,
        symbol,
        limit=None,
    ):
        self.timestamp += 1

        books = {
            "BTC/USDT": {
                "bids": [[61900.0, 10.0]],
                "asks": [[62000.0, 10.0]],
            },
            "ETH/BTC": {
                "bids": [[0.049, 100.0]],
                "asks": [[0.05, 100.0]],
            },
            "ETH/USDT": {
                "bids": [[3300.0, 100.0]],
                "asks": [[3310.0, 100.0]],
            },
        }

        book = books[symbol]

        return {
            "symbol": symbol,
            "bids": book["bids"],
            "asks": book["asks"],
            "timestamp": self.timestamp,
        }


def permission():
    return {
        "permission_id": "PERM-174",
        "route_id": "ROUTE-001",
        "approval_id": "ARB-174",
        "asset": "BTC",
        "trade_amount": 250.0,
        "permission_granted": True,
        "status": (
            "execution_permission_granted"
        ),
        "live_order_submitted": False,
    }


def route():
    return {
        "route_id": "ROUTE-001",
        "legs": [
            {
                "symbol": "BTC/USDT",
                "side": "buy",
            },
            {
                "symbol": "ETH/BTC",
                "side": "buy",
            },
            {
                "symbol": "ETH/USDT",
                "side": "sell",
            },
        ],
    }


def portfolio():
    return {
        "total_capital": 1000.0,
        "reserved_capital": 0.0,
        "asset_exposure": {
            "BTC": 0.10,
        },
        "max_asset_exposure": 0.25,
        "open_routes": 0,
        "max_open_routes": 3,
    }


def source_networks():
    return [
        NetworkInfo(
            "USDT",
            "TRC20",
            withdraw_fee=1.0,
            min_withdraw=10.0,
        ),
    ]


def destination_networks():
    return [
        NetworkInfo(
            "USDT",
            "TRC20",
        ),
    ]


def circuit_allowed():
    return {
        "allowed": True,
        "state": "CLOSED",
        "reason": None,
    }


def portfolio_allowed():
    return {
        "approved": True,
        "reason": None,
        "available_capital": 1000.0,
        "projected_asset_exposure": 0.10,
        "open_routes": 0,
    }


def controller():
    return (
        EndToEndLiveMarketPaperCycleController(
            FakeSnapshotEngine()
        )
    )


def run(
    permission_result=None,
    successful_test_count=0,
    repeat_count=0,
    scale_count=0,
    max_repeats=5,
    max_scale_steps=2,
    max_cumulative_trade_amount=2000.0,
    circuit=None,
    portfolio_risk=None,
):
    return controller().run_cycle(
        permission_result=(
            permission()
            if permission_result is None
            else permission_result
        ),
        execution_id="EXEC-174-001",
        route=route(),
        portfolio=portfolio(),
        asset="BTC",
        additional_exposure=0.05,
        starting_value=250.0,
        successful_test_count=(
            successful_test_count
        ),
        required_successes_for_scale=2,
        scale_multiplier=2.0,
        min_trade_size=100.0,
        max_trade_size=1000.0,
        repeat_count=repeat_count,
        scale_count=scale_count,
        cumulative_trade_amount=250.0,
        max_repeats=max_repeats,
        max_scale_steps=max_scale_steps,
        max_cumulative_trade_amount=(
            max_cumulative_trade_amount
        ),
        circuit_breaker_result=(
            circuit_allowed()
            if circuit is None
            else circuit
        ),
        portfolio_risk_result=(
            portfolio_allowed()
            if portfolio_risk is None
            else portfolio_risk
        ),
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
        buy_exchange="kucoin",
        sell_exchange="gate",
        expected_profit=5.0,
        estimated_fees=0.5,
        slippage_allowance=0.25,
        minimum_profit_percent=2.0,
    )


def test_complete_cycle_runs_end_to_end():
    result = run()

    assert result["cycle_complete"] is True
    assert (
        result["reason"]
        == "end_to_end_live_market_paper_cycle_complete"
    )


def test_execution_stage_completes():
    result = run()

    execution = result[
        "execution_result"
    ]

    assert execution["executed"] is True
    assert execution["status"] == "COMPLETED"


def test_feedback_stage_completes():
    result = run()

    feedback = result[
        "feedback_result"
    ]

    assert feedback["feedback_complete"] is True
    assert (
        feedback["validation_result"][
            "validated"
        ]
        is True
    )


def test_profitable_cycle_prepares_repeat():
    result = run()

    continuation = result[
        "continuation_result"
    ]

    assert (
        continuation["continuation_ready"]
        is True
    )
    assert (
        continuation["decision"]
        == "REPEAT_SAME_SIZE"
    )


def test_success_threshold_can_prepare_scale():
    result = run(
        successful_test_count=2
    )

    continuation = result[
        "continuation_result"
    ]

    assert (
        continuation["continuation_ready"]
        is True
    )
    assert continuation["decision"] == "SCALE_UP"
    assert continuation["trade_amount"] == 500.0


def test_next_cycle_stops_at_fresh_approval():
    result = run()

    assert result["next_cycle_ready"] is True
    assert (
        result["stage"]
        == "AWAITING_FRESH_APPROVAL"
    )

    continuation = result[
        "continuation_result"
    ]

    assert (
        continuation["manual_approval_required"]
        is True
    )
    assert (
        continuation["approval_granted"]
        is False
    )


def test_fresh_execution_permission_is_still_required():
    result = run()

    continuation = result[
        "continuation_result"
    ]

    assert (
        continuation[
            "fresh_execution_permission_required"
        ]
        is True
    )
    assert (
        continuation["permission_granted"]
        is False
    )


def test_invalid_permission_stops_at_execution():
    denied = permission()
    denied["permission_granted"] = False

    result = run(
        permission_result=denied
    )

    assert result["cycle_complete"] is False
    assert result["stage"] == "EXECUTION"
    assert (
        result["reason"]
        == "execution_permission_required"
    )


def test_live_permission_is_blocked():
    denied = permission()
    denied["live_order_submitted"] = True

    result = run(
        permission_result=denied
    )

    assert result["cycle_complete"] is False
    assert (
        result["reason"]
        == "live_order_already_submitted"
    )


def test_repeat_limit_produces_hard_stop():
    result = run(
        repeat_count=5,
        max_repeats=5,
    )

    assert result["cycle_complete"] is True
    assert result["hard_stop"] is True

    continuation = result[
        "continuation_result"
    ]

    assert (
        continuation["reason"]
        == "maximum_repeat_count_reached"
    )


def test_scale_limit_falls_back_to_repeat():
    result = run(
        successful_test_count=2,
        scale_count=2,
        max_scale_steps=2,
    )

    continuation = result[
        "continuation_result"
    ]

    assert (
        continuation["continuation_ready"]
        is True
    )
    assert (
        continuation["scale_suppressed"]
        is True
    )
    assert (
        continuation["decision"]
        == "REPEAT_SAME_SIZE"
    )


def test_open_circuit_produces_hard_stop():
    result = run(
        circuit={
            "allowed": False,
            "state": "OPEN",
            "reason": "circuit_open",
        }
    )

    assert result["hard_stop"] is True
    assert (
        result["continuation_result"][
            "reason"
        ]
        == "execution_circuit_open"
    )


def test_portfolio_rejection_produces_hard_stop():
    result = run(
        portfolio_risk={
            "approved": False,
            "reason": (
                "asset_exposure_exceeded"
            ),
        }
    )

    assert result["hard_stop"] is True
    assert (
        result["continuation_result"][
            "reason"
        ]
        == "asset_exposure_exceeded"
    )


def test_execution_ids_are_preserved():
    result = run()

    assert result["route_id"] == "ROUTE-001"
    assert result["approval_id"] == "ARB-174"
    assert result["permission_id"] == "PERM-174"


def test_pnl_is_available_at_top_level_path():
    result = run()

    pnl = (
        result["feedback_result"]
        ["pnl_result"]["pnl"]
    )

    assert pnl["starting_value"] == 250.0
    assert pnl["gross_final_value"] > 0


def test_capital_reservation_is_released():
    service = controller()

    result = service.run_cycle(
        permission_result=permission(),
        execution_id="EXEC-174-002",
        route=route(),
        portfolio=portfolio(),
        asset="BTC",
        additional_exposure=0.05,
        starting_value=250.0,
        successful_test_count=0,
        required_successes_for_scale=2,
        scale_multiplier=2.0,
        min_trade_size=100.0,
        max_trade_size=1000.0,
        repeat_count=0,
        scale_count=0,
        cumulative_trade_amount=250.0,
        max_repeats=5,
        max_scale_steps=2,
        max_cumulative_trade_amount=2000.0,
        circuit_breaker_result=circuit_allowed(),
        portfolio_risk_result=portfolio_allowed(),
        source_networks=source_networks(),
        destination_networks=destination_networks(),
        transfer_amount=250.0,
        available_liquidity=10000.0,
        minimum_liquidity_ratio=0.1,
        expected_price=100.0,
        current_price=99.5,
        max_slippage_percent=1.0,
        buy_exchange="kucoin",
        sell_exchange="gate",
        expected_profit=5.0,
        estimated_fees=0.5,
        slippage_allowance=0.25,
        minimum_profit_percent=2.0,
    )

    assert result["cycle_complete"] is True
    assert service.total_reserved() == 0.0


def test_cycle_is_recorded_in_history():
    service = controller()

    service.run_cycle(
        permission_result=permission(),
        execution_id="EXEC-174-003",
        route=route(),
        portfolio=portfolio(),
        asset="BTC",
        additional_exposure=0.05,
        starting_value=250.0,
        successful_test_count=0,
        required_successes_for_scale=2,
        scale_multiplier=2.0,
        min_trade_size=100.0,
        max_trade_size=1000.0,
        repeat_count=0,
        scale_count=0,
        cumulative_trade_amount=250.0,
        max_repeats=5,
        max_scale_steps=2,
        max_cumulative_trade_amount=2000.0,
        circuit_breaker_result=circuit_allowed(),
        portfolio_risk_result=portfolio_allowed(),
        source_networks=source_networks(),
        destination_networks=destination_networks(),
        transfer_amount=250.0,
        available_liquidity=10000.0,
        minimum_liquidity_ratio=0.1,
        expected_price=100.0,
        current_price=99.5,
        max_slippage_percent=1.0,
        buy_exchange="kucoin",
        sell_exchange="gate",
        expected_profit=5.0,
        estimated_fees=0.5,
        slippage_allowance=0.25,
        minimum_profit_percent=2.0,
    )

    assert len(service.history()) == 1


def test_missing_permission_is_rejected():
    with pytest.raises(
        ValueError,
        match="permission_result is required",
    ):
        controller().run_cycle(
            permission_result=None,
            execution_id="EXEC-174-004",
            route=route(),
            portfolio=portfolio(),
            asset="BTC",
            additional_exposure=0.05,
            starting_value=250.0,
            successful_test_count=0,
            required_successes_for_scale=2,
            scale_multiplier=2.0,
            min_trade_size=100.0,
            max_trade_size=1000.0,
            repeat_count=0,
            scale_count=0,
            cumulative_trade_amount=250.0,
            max_repeats=5,
            max_scale_steps=2,
            max_cumulative_trade_amount=2000.0,
            circuit_breaker_result=circuit_allowed(),
            portfolio_risk_result=portfolio_allowed(),
            source_networks=source_networks(),
            destination_networks=destination_networks(),
            transfer_amount=250.0,
            available_liquidity=10000.0,
            minimum_liquidity_ratio=0.1,
            expected_price=100.0,
            current_price=99.5,
            max_slippage_percent=1.0,
            buy_exchange="kucoin",
            sell_exchange="gate",
            expected_profit=5.0,
            estimated_fees=0.5,
            slippage_allowance=0.25,
        )


def test_snapshot_engine_is_required():
    with pytest.raises(
        ValueError,
        match="snapshot_engine is required",
    ):
        EndToEndLiveMarketPaperCycleController(
            None
        )


def test_every_stage_remains_paper_only():
    result = run()

    assert result["test_trade"] is True
    assert result["simulated"] is True
    assert result["paper_trade"] is True
    assert result["live_order_submitted"] is False

    assert (
        result["execution_result"][
            "live_order_submitted"
        ]
        is False
    )
    assert (
        result["feedback_result"][
            "live_order_submitted"
        ]
        is False
    )
    assert (
        result["continuation_result"][
            "live_order_submitted"
        ]
        is False
    )


# EX-349 — fresh repeat/scale market provenance


class ChangingMarketSnapshotEngine:
    """
    First capture represents the executable paper trade.

    Any later capture represents the genuinely fresh market
    state that must be used before another approval request.
    """

    def __init__(
        self,
        second_market_liquidity=True,
    ):
        self.calls = []
        self.timestamp = 1000
        self.second_market_liquidity = (
            second_market_liquidity
        )

    def snapshot(
        self,
        symbol,
        limit=None,
    ):
        self.calls.append(symbol)
        self.timestamp += 1

        capture_number = (
            (len(self.calls) - 1) // 3
        ) + 1

        if capture_number == 1:
            books = {
                "BTC/USDT": {
                    "bids": [[61900.0, 10.0]],
                    "asks": [[62000.0, 10.0]],
                },
                "ETH/BTC": {
                    "bids": [[0.049, 100.0]],
                    "asks": [[0.05, 100.0]],
                },
                "ETH/USDT": {
                    "bids": [[3300.0, 100.0]],
                    "asks": [[3310.0, 100.0]],
                },
            }
        elif self.second_market_liquidity:
            books = {
                "BTC/USDT": {
                    "bids": [[61890.0, 10.0]],
                    "asks": [[62010.0, 10.0]],
                },
                "ETH/BTC": {
                    "bids": [[0.0489, 100.0]],
                    "asks": [[0.0501, 100.0]],
                },
                "ETH/USDT": {
                    "bids": [[3295.0, 100.0]],
                    "asks": [[3315.0, 100.0]],
                },
            }
        else:
            # Deliberately inadequate fresh depth.
            # Caller-supplied "available_liquidity=10000"
            # must not be able to override this.
            books = {
                "BTC/USDT": {
                    "bids": [[61890.0, 0.00001]],
                    "asks": [[62010.0, 0.00001]],
                },
                "ETH/BTC": {
                    "bids": [[0.0489, 0.00001]],
                    "asks": [[0.0501, 0.00001]],
                },
                "ETH/USDT": {
                    "bids": [[3295.0, 0.00001]],
                    "asks": [[3315.0, 0.00001]],
                },
            }

        book = books[symbol]

        return {
            "exchange_id": "kucoin",
            "symbol": symbol,
            "bids": book["bids"],
            "asks": book["asks"],
            "best_bid": book["bids"][0][0],
            "best_ask": book["asks"][0][0],
            "timestamp": self.timestamp,
            "sequence": len(self.calls),
            "paper_only": True,
            "live_order_submitted": False,
        }


def run_with_snapshot_engine(
    snapshot_engine,
    *,
    available_liquidity=10000.0,
    expected_price=100.0,
    current_price=99.5,
):
    service = (
        EndToEndLiveMarketPaperCycleController(
            snapshot_engine
        )
    )

    return service.run_cycle(
        permission_result=permission(),
        execution_id="EXEC-349-001",
        route=route(),
        portfolio=portfolio(),
        asset="BTC",
        additional_exposure=0.05,
        starting_value=250.0,
        successful_test_count=0,
        required_successes_for_scale=2,
        scale_multiplier=2.0,
        min_trade_size=100.0,
        max_trade_size=1000.0,
        repeat_count=0,
        scale_count=0,
        cumulative_trade_amount=250.0,
        max_repeats=5,
        max_scale_steps=2,
        max_cumulative_trade_amount=2000.0,
        circuit_breaker_result=circuit_allowed(),
        portfolio_risk_result=portfolio_allowed(),
        source_networks=source_networks(),
        destination_networks=destination_networks(),
        transfer_amount=250.0,
        available_liquidity=available_liquidity,
        minimum_liquidity_ratio=0.1,
        expected_price=expected_price,
        current_price=current_price,
        max_slippage_percent=1.0,
        buy_exchange="kucoin",
        sell_exchange="gate",
        expected_profit=5.0,
        estimated_fees=0.5,
        slippage_allowance=0.25,
        minimum_profit_percent=2.0,
    )


def test_repeat_scale_requires_second_fresh_market_capture():
    snapshots = ChangingMarketSnapshotEngine()

    result = run_with_snapshot_engine(
        snapshots
    )

    assert result["cycle_complete"] is True

    # Three route legs were required for the completed paper
    # execution. A next-cycle approval must use another
    # independent market capture, not reuse those observations.
    assert len(snapshots.calls) >= 6

    assert snapshots.calls[:3] == [
        "BTC/USDT",
        "ETH/BTC",
        "ETH/USDT",
    ]

    assert snapshots.calls[3:6] == [
        "BTC/USDT",
        "ETH/BTC",
        "ETH/USDT",
    ]


def test_caller_liquidity_cannot_override_fresh_order_book():
    snapshots = ChangingMarketSnapshotEngine(
        second_market_liquidity=False
    )

    result = run_with_snapshot_engine(
        snapshots,
        # Deliberately dishonest optimistic value.
        available_liquidity=1_000_000_000.0,
    )

    continuation = result[
        "continuation_result"
    ]

    assert (
        continuation["continuation_ready"]
        is False
    )
    assert (
        continuation["stage"]
        == "NEXT_CYCLE"
    )
    assert continuation["hard_stop"] is False
    assert (
        continuation["reason"]
        == "liquidity_revalidation_failed"
    )

    next_cycle = continuation[
        "next_cycle"
    ]

    assert (
        next_cycle["stage"]
        == "REVALIDATION"
    )
    assert (
        next_cycle["reason"]
        == "liquidity_revalidation_failed"
    )
    assert (
        next_cycle[
            "revalidation_result"
        ]["revalidated"]
        is False
    )
    assert (
        next_cycle[
            "revalidation_result"
        ]["allowed"]
        is False
    )

    assert len(snapshots.calls) >= 6


def test_repeat_scale_result_contains_market_provenance():
    snapshots = ChangingMarketSnapshotEngine()

    result = run_with_snapshot_engine(
        snapshots
    )

    continuation = result[
        "continuation_result"
    ]

    provenance = continuation[
        "market_provenance"
    ]

    assert provenance["route_id"] == "ROUTE-001"

    assert provenance[
        "independent_revalidation_capture"
    ] is True

    assert provenance[
        "snapshot_age_verified"
    ] is False

    assert provenance[
        "snapshot_count"
    ] == 3

    assert provenance[
        "symbols"
    ] == [
        "BTC/USDT",
        "ETH/BTC",
        "ETH/USDT",
    ]

    assert (
        provenance["latest_timestamp"]
        >= provenance["earliest_timestamp"]
    )


def test_provenance_market_data_is_separate_from_execution_capture():
    snapshots = ChangingMarketSnapshotEngine()

    result = run_with_snapshot_engine(
        snapshots
    )

    provenance = result[
        "continuation_result"
    ]["market_provenance"]

    # Fresh revalidation must be based on observations taken
    # after the execution-stage market capture.
    assert provenance[
        "earliest_timestamp"
    ] >= 1004


def test_caller_price_cannot_be_only_source_of_revalidation_truth():
    snapshots = ChangingMarketSnapshotEngine()

    result = run_with_snapshot_engine(
        snapshots,
        # These deliberately have no relationship to the
        # BTC/USDT / ETH/BTC / ETH/USDT books above.
        expected_price=1.0,
        current_price=1.0,
    )

    provenance = result[
        "continuation_result"
    ]["market_provenance"]

    assert (
        provenance[
            "market_inputs_derived_from_snapshot"
        ]
        is True
    )

    assert provenance[
        "caller_market_values_authoritative"
    ] is False


def test_market_provenance_remains_paper_only():
    snapshots = ChangingMarketSnapshotEngine()

    result = run_with_snapshot_engine(
        snapshots
    )

    provenance = result[
        "continuation_result"
    ]["market_provenance"]

    assert provenance["paper_only"] is True
    assert provenance["live_order_submitted"] is False
