import pytest

from core.exchange_subscription_capacity_profiles import (
    ExchangeSubscriptionCapacityProfiles,
)
from core.hundred_coin_public_paper_scan_harness import (
    HundredCoinPublicPaperScanHarness,
)


class FakeScanner:
    def __init__(
        self,
        live_order_submitted=False,
    ):
        self.calls = []
        self._live_order_submitted = (
            live_order_submitted
        )

    def scan(
        self,
        exchange_coin_assets,
        fee_rates,
        starting_usdt_value,
        max_slippage_percent,
    ):
        self.calls.append({
            "exchange_coin_assets": {
                exchange_id: set(coins)
                for exchange_id, coins in (
                    exchange_coin_assets.items()
                )
            },
            "fee_rates": dict(
                fee_rates
            ),
            "starting_usdt_value": (
                starting_usdt_value
            ),
            "max_slippage_percent": (
                max_slippage_percent
            ),
        })

        return {
            "best_route": None,
            "ranked_routes": [],
            "route_count": 0,
            "failure_count": 0,
            "paper_only": True,
            "live_order_submitted": (
                self._live_order_submitted
            ),
        }


def capacity_profiles(
    capacity=10,
):
    registry = (
        ExchangeSubscriptionCapacityProfiles()
    )

    for exchange_id in (
        "kucoin",
        "gate",
        "bitget",
    ):
        registry.register({
            "exchange_id": exchange_id,
            "max_symbols_per_batch": (
                capacity
            ),
            "max_batches": 1,
        })

    return registry


def run_harness(
    exchange_coin_assets,
    *,
    requested_coin_count=3,
    capacity=10,
    scanner=None,
):
    scanner = scanner or FakeScanner()

    harness = (
        HundredCoinPublicPaperScanHarness(
            scanner=scanner,
            capacity_profiles=(
                capacity_profiles(
                    capacity=capacity
                )
            ),
        )
    )

    result = harness.run(
        exchange_coin_assets=(
            exchange_coin_assets
        ),
        fee_rates={
            "kucoin": 0.001,
            "gate": 0.001,
            "bitget": 0.001,
        },
        starting_usdt_value=100.0,
        max_slippage_percent=0.5,
        requested_coin_count=(
            requested_coin_count
        ),
    )

    return result, scanner


def test_runs_exact_globally_approved_universe():
    result, scanner = run_harness({
        "kucoin": {
            "BTC",
            "ETH",
            "SOL",
            "XRP",
        },
        "gate": {
            "BTC",
            "ETH",
            "SOL",
            "DOGE",
        },
        "bitget": {
            "BTC",
            "ETH",
            "XRP",
        },
    })

    assert result["harness_ready"] is True
    assert result["scan_executed"] is True
    assert result["readiness"] == "PASS"

    assert result[
        "approved_coin_assets"
    ] == [
        "BTC",
        "ETH",
        "SOL",
    ]

    assert len(scanner.calls) == 1

    assert scanner.calls[0][
        "exchange_coin_assets"
    ] == {
        "kucoin": {
            "BTC",
            "ETH",
            "SOL",
        },
        "gate": {
            "BTC",
            "ETH",
            "SOL",
        },
        "bitget": {
            "BTC",
            "ETH",
        },
    }


def test_scanner_cannot_receive_unapproved_coin():
    result, scanner = run_harness({
        "kucoin": {
            "BTC",
            "ETH",
            "SOL",
            "ONLYK",
        },
        "gate": {
            "BTC",
            "ETH",
            "SOL",
            "ONLYG",
        },
    })

    sent = scanner.calls[0][
        "exchange_coin_assets"
    ]

    all_sent = {
        coin
        for coins in sent.values()
        for coin in coins
    }

    assert all_sent == {
        "BTC",
        "ETH",
        "SOL",
    }

    assert "ONLYK" not in all_sent
    assert "ONLYG" not in all_sent

    assert result[
        "approved_coin_count"
    ] == 3


def test_universe_failure_blocks_scanner():
    result, scanner = run_harness(
        {
            "kucoin": {
                "BTC",
                "ONLYK",
            },
            "gate": {
                "BTC",
                "ONLYG",
            },
        },
        requested_coin_count=2,
    )

    assert result[
        "harness_ready"
    ] is False

    assert result[
        "scan_executed"
    ] is False

    assert result["reason"] == (
        "insufficient_cross_exchange_coin_coverage"
    )

    assert scanner.calls == []


def test_capacity_failure_blocks_scanner():
    result, scanner = run_harness(
        {
            "kucoin": {
                "BTC",
                "ETH",
                "SOL",
            },
            "gate": {
                "BTC",
                "ETH",
                "SOL",
            },
        },
        capacity=2,
    )

    assert result[
        "harness_ready"
    ] is False

    assert result[
        "scan_executed"
    ] is False

    assert result["reason"] == (
        "feed_capacity_exceeded"
    )

    assert scanner.calls == []


def test_live_order_signal_fails_harness():
    scanner = FakeScanner(
        live_order_submitted=True,
    )

    result, scanner = run_harness(
        {
            "kucoin": {
                "BTC",
                "ETH",
                "SOL",
            },
            "gate": {
                "BTC",
                "ETH",
                "SOL",
            },
        },
        scanner=scanner,
    )

    assert result[
        "harness_ready"
    ] is False

    assert result[
        "scan_executed"
    ] is True

    assert result["reason"] == (
        "live_order_submission_detected"
    )

    assert (
        result["live_order_submitted"]
        is True
    )


def test_harness_result_is_paper_only():
    result, _ = run_harness({
        "kucoin": {
            "BTC",
            "ETH",
            "SOL",
        },
        "gate": {
            "BTC",
            "ETH",
            "SOL",
        },
    })

    assert result["paper_only"] is True
    assert (
        result["live_order_submitted"]
        is False
    )


def test_fee_rate_required_for_approved_exchange():
    registry = capacity_profiles()
    scanner = FakeScanner()

    harness = (
        HundredCoinPublicPaperScanHarness(
            scanner=scanner,
            capacity_profiles=registry,
        )
    )

    with pytest.raises(
        ValueError,
        match=(
            "fee rate is required "
            "for exchange: gate"
        ),
    ):
        harness.run(
            exchange_coin_assets={
                "kucoin": {
                    "BTC",
                },
                "gate": {
                    "BTC",
                },
            },
            fee_rates={
                "kucoin": 0.001,
            },
            starting_usdt_value=100.0,
            max_slippage_percent=0.5,
            requested_coin_count=1,
        )

    assert scanner.calls == []


def test_scanner_is_required():
    with pytest.raises(
        ValueError,
        match="scanner is required",
    ):
        HundredCoinPublicPaperScanHarness(
            scanner=None,
            capacity_profiles=(
                capacity_profiles()
            ),
        )


def test_capacity_profiles_are_required():
    with pytest.raises(
        ValueError,
        match=(
            "capacity_profiles are required"
        ),
    ):
        HundredCoinPublicPaperScanHarness(
            scanner=FakeScanner(),
            capacity_profiles=None,
        )


def test_fee_rates_are_required():
    harness = (
        HundredCoinPublicPaperScanHarness(
            scanner=FakeScanner(),
            capacity_profiles=(
                capacity_profiles()
            ),
        )
    )

    with pytest.raises(
        ValueError,
        match="fee_rates are required",
    ):
        harness.run(
            exchange_coin_assets={
                "kucoin": {"BTC"},
                "gate": {"BTC"},
            },
            fee_rates=None,
            starting_usdt_value=100.0,
            max_slippage_percent=0.5,
            requested_coin_count=1,
        )


def test_starting_value_must_be_positive():
    harness = (
        HundredCoinPublicPaperScanHarness(
            scanner=FakeScanner(),
            capacity_profiles=(
                capacity_profiles()
            ),
        )
    )

    with pytest.raises(
        ValueError,
        match=(
            "starting_usdt_value "
            "must be positive"
        ),
    ):
        harness.run(
            exchange_coin_assets={
                "kucoin": {"BTC"},
                "gate": {"BTC"},
            },
            fee_rates={
                "kucoin": 0.001,
                "gate": 0.001,
            },
            starting_usdt_value=0,
            max_slippage_percent=0.5,
            requested_coin_count=1,
        )
