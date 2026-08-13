import pytest

from core.external_arbitrage_verification_bridge import (
    ExternalArbitrageVerificationBridge,
)


def candidate():
    return {
        "opportunity_key": "COTI:kucoin:digifinex",
        "source": "coinmarketgap",
        "source_signal_id": "CMG-001",
        "coin": "COTI",
        "buy_exchange": "kucoin",
        "sell_exchange": "digifinex",
        "reported_status": "exploitable",
        "reported_spread_percent": 12.62,
        "arbos_verified": False,
        "executable": False,
        "verification_required": True,
    }


class FakeRunner:
    def __init__(self, result):
        self.result = result
        self.calls = []

    def run(
        self,
        source_exchange_id,
        destination_exchange_id,
        scan_kwargs=None,
        prepare_kwargs=None,
    ):
        self.calls.append({
            "source_exchange_id": source_exchange_id,
            "destination_exchange_id": destination_exchange_id,
            "scan_kwargs": scan_kwargs,
            "prepare_kwargs": prepare_kwargs,
        })

        return self.result


class FakeTracker:
    def __init__(self):
        self.calls = []

    def record_verification(
        self,
        opportunity_key,
        verified,
        executable,
    ):
        self.calls.append({
            "opportunity_key": opportunity_key,
            "verified": verified,
            "executable": executable,
        })

        return {
            "opportunity_key": opportunity_key,
            "arbos_verified": verified,
            "executable": executable,
        }


def test_external_candidate_is_sent_to_existing_live_paper_runner():
    runner = FakeRunner({
        "scan_complete": True,
        "best_cross_exchange": {
            "executable": True,
            "net_profit_percent": 2.5,
        },
        "paper_only": True,
        "live_order_submitted": False,
    })

    tracker = FakeTracker()

    bridge = ExternalArbitrageVerificationBridge(
        runner=runner,
        tracker=tracker,
    )

    bridge.verify(
        candidate(),
        starting_usdt_value=300.0,
        source_fee_rate=0.001,
        destination_fee_rate=0.001,
        max_slippage_percent=0.5,
        minimum_profit_percent=0.5,
    )

    call = runner.calls[0]

    assert call[
        "source_exchange_id"
    ] == "kucoin"

    assert call[
        "destination_exchange_id"
    ] == "digifinex"

    assert call[
        "prepare_kwargs"
    ]["coin_asset"] == "COTI"

    assert call[
        "prepare_kwargs"
    ]["starting_usdt_value"] == 300.0


def test_successful_existing_pipeline_result_verifies_candidate():
    runner = FakeRunner({
        "scan_complete": True,
        "best_cross_exchange": {
            "route_id": (
                "DIRECT-kucoin-COTI-digifinex"
            ),
            "executable": True,
            "net_profit": 7.5,
            "net_profit_percent": 2.5,
        },
        "paper_only": True,
        "live_order_submitted": False,
    })

    tracker = FakeTracker()

    result = ExternalArbitrageVerificationBridge(
        runner=runner,
        tracker=tracker,
    ).verify(
        candidate(),
        starting_usdt_value=300.0,
        source_fee_rate=0.001,
        destination_fee_rate=0.001,
    )

    assert result["arbos_verified"] is True
    assert result["executable"] is True

    assert result[
        "verification_required"
    ] is False

    assert result[
        "verified_net_profit_percent"
    ] == 2.5

    assert tracker.calls[0] == {
        "opportunity_key": (
            "COTI:kucoin:digifinex"
        ),
        "verified": True,
        "executable": True,
    }


def test_external_exploitable_claim_does_not_override_failed_verification():
    runner = FakeRunner({
        "scan_complete": True,
        "best_cross_exchange": None,
        "rejected_cross_exchange": [
            {
                "reason": (
                    "no_compatible_network"
                ),
            },
        ],
        "paper_only": True,
        "live_order_submitted": False,
    })

    tracker = FakeTracker()

    result = ExternalArbitrageVerificationBridge(
        runner=runner,
        tracker=tracker,
    ).verify(
        candidate(),
        starting_usdt_value=300.0,
        source_fee_rate=0.001,
        destination_fee_rate=0.001,
    )

    assert result[
        "reported_status"
    ] == "exploitable"

    assert result[
        "arbos_verified"
    ] is False

    assert result[
        "executable"
    ] is False

    assert result[
        "verification_required"
    ] is False


def test_non_executable_best_route_is_not_verified():
    runner = FakeRunner({
        "scan_complete": True,
        "best_cross_exchange": {
            "executable": False,
            "reason": "slippage_exceeded",
        },
        "paper_only": True,
        "live_order_submitted": False,
    })

    result = ExternalArbitrageVerificationBridge(
        runner=runner,
        tracker=FakeTracker(),
    ).verify(
        candidate(),
        starting_usdt_value=300.0,
        source_fee_rate=0.001,
        destination_fee_rate=0.001,
    )

    assert result["arbos_verified"] is False
    assert result["executable"] is False


def test_runner_failure_is_recorded_as_failed_verification():
    runner = FakeRunner({
        "scan_complete": False,
        "reason": "prepare_failed",
        "paper_only": True,
        "live_order_submitted": False,
    })

    tracker = FakeTracker()

    result = ExternalArbitrageVerificationBridge(
        runner=runner,
        tracker=tracker,
    ).verify(
        candidate(),
        starting_usdt_value=300.0,
        source_fee_rate=0.001,
        destination_fee_rate=0.001,
    )

    assert result["arbos_verified"] is False
    assert result["executable"] is False

    assert tracker.calls[0][
        "verified"
    ] is False


def test_required_candidate_fields_are_validated():
    bridge = ExternalArbitrageVerificationBridge(
        runner=FakeRunner({}),
        tracker=FakeTracker(),
    )

    bad = candidate()
    bad["coin"] = ""

    with pytest.raises(
        ValueError,
        match="coin is required",
    ):
        bridge.verify(
            bad,
            starting_usdt_value=300.0,
            source_fee_rate=0.001,
            destination_fee_rate=0.001,
        )


def test_bridge_is_paper_safe():
    runner = FakeRunner({
        "scan_complete": True,
        "best_cross_exchange": None,
        "paper_only": True,
        "live_order_submitted": False,
    })

    result = ExternalArbitrageVerificationBridge(
        runner=runner,
        tracker=FakeTracker(),
    ).verify(
        candidate(),
        starting_usdt_value=300.0,
        source_fee_rate=0.001,
        destination_fee_rate=0.001,
    )

    assert result["paper_only"] is True

    assert result[
        "live_order_submitted"
    ] is False
