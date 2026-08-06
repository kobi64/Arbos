import pytest

from core.venue_aware_dynamic_fee_depth_scanner import (
    VenueAwareDynamicFeeDepthScanner,
)


class FakeFeeResolver:
    def resolve(self, exchange_id, fee_type="taker"):
        fees = {
            "kraken": 0.004,
            "kucoin": 0.001,
        }

        return {
            "exchange_id": exchange_id,
            "fee_type": fee_type,
            "fee_rate": fees[exchange_id],
        }


class FakeDepthScanner:
    def __init__(self, venue):
        self.venue = venue
        self.calls = []

    def scan_route(
        self,
        route,
        starting_value,
        fee_rate,
        max_slippage_percent,
    ):
        self.calls.append({
            "route": route,
            "starting_value": starting_value,
            "fee_rate": fee_rate,
            "max_slippage_percent": max_slippage_percent,
        })

        return {
            "route_id": route["route_id"],
            "filled": True,
            "net_profit_percent": (
                -1.2 if self.venue == "kraken" else -0.4
            ),
            "paper_only": True,
            "live_order_submitted": False,
        }


def test_dispatches_to_correct_venue_depth_scanner():
    kraken_scanner = FakeDepthScanner("kraken")
    kucoin_scanner = FakeDepthScanner("kucoin")

    scanner = VenueAwareDynamicFeeDepthScanner(
        fee_resolver=FakeFeeResolver(),
        depth_scanners={
            "kraken": kraken_scanner,
            "kucoin": kucoin_scanner,
        },
    )

    result = scanner.scan_route(
        exchange_id="kucoin",
        route={"route_id": "R1", "legs": []},
        starting_value=100.0,
        max_slippage_percent=0.5,
    )

    assert result["exchange_id"] == "kucoin"
    assert result["resolved_fee_rate"] == 0.001
    assert len(kucoin_scanner.calls) == 1
    assert len(kraken_scanner.calls) == 0


def test_passes_resolved_fee_to_selected_depth_scanner():
    kraken_scanner = FakeDepthScanner("kraken")

    scanner = VenueAwareDynamicFeeDepthScanner(
        fee_resolver=FakeFeeResolver(),
        depth_scanners={
            "kraken": kraken_scanner,
        },
    )

    scanner.scan_route(
        exchange_id="kraken",
        route={"route_id": "R2", "legs": []},
        starting_value=100.0,
        max_slippage_percent=0.5,
    )

    assert kraken_scanner.calls[0]["fee_rate"] == 0.004
