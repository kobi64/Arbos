import pytest

from core.dynamic_fee_depth_aware_scanner import (
    DynamicFeeDepthAwareScanner,
)


class FakeFeeResolver:
    def resolve(self, exchange_id, fee_type="taker"):
        return {
            "exchange_id": exchange_id,
            "fee_type": fee_type,
            "fee_rate": 0.004,
        }


class FakeDepthScanner:
    def __init__(self):
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
            "net_final_value": 98.8,
            "net_profit": -1.2,
            "net_profit_percent": -1.2,
            "paper_only": True,
            "live_order_submitted": False,
        }


def test_resolves_fee_and_runs_depth_scanner():
    fee_resolver = FakeFeeResolver()
    depth_scanner = FakeDepthScanner()

    scanner = DynamicFeeDepthAwareScanner(
        fee_resolver=fee_resolver,
        depth_scanner=depth_scanner,
    )

    route = {
        "route_id": "ROUTE-001",
        "legs": [],
    }

    result = scanner.scan_route(
        exchange_id="kraken",
        route=route,
        starting_value=100.0,
        max_slippage_percent=0.5,
    )

    assert result["route_id"] == "ROUTE-001"
    assert depth_scanner.calls[0]["fee_rate"] == 0.004
    assert depth_scanner.calls[0]["starting_value"] == 100.0
    assert depth_scanner.calls[0]["max_slippage_percent"] == 0.5


def test_defaults_to_taker_fee_type():
    class RecordingFeeResolver:
        def __init__(self):
            self.fee_type = None

        def resolve(self, exchange_id, fee_type="taker"):
            self.fee_type = fee_type
            return {
                "exchange_id": exchange_id,
                "fee_type": fee_type,
                "fee_rate": 0.004,
            }

    resolver = RecordingFeeResolver()
    scanner = DynamicFeeDepthAwareScanner(
        fee_resolver=resolver,
        depth_scanner=FakeDepthScanner(),
    )

    scanner.scan_route(
        exchange_id="kraken",
        route={"route_id": "ROUTE-002", "legs": []},
        starting_value=100.0,
        max_slippage_percent=0.5,
    )

    assert resolver.fee_type == "taker"


def test_can_request_maker_fee_type():
    class RecordingFeeResolver:
        def __init__(self):
            self.fee_type = None

        def resolve(self, exchange_id, fee_type="taker"):
            self.fee_type = fee_type
            return {
                "exchange_id": exchange_id,
                "fee_type": fee_type,
                "fee_rate": 0.0025,
            }

    resolver = RecordingFeeResolver()
    scanner = DynamicFeeDepthAwareScanner(
        fee_resolver=resolver,
        depth_scanner=FakeDepthScanner(),
    )

    scanner.scan_route(
        exchange_id="kraken",
        route={"route_id": "ROUTE-003", "legs": []},
        starting_value=100.0,
        max_slippage_percent=0.5,
        fee_type="maker",
    )

    assert resolver.fee_type == "maker"


def test_missing_exchange_id_is_rejected():
    scanner = DynamicFeeDepthAwareScanner(
        fee_resolver=FakeFeeResolver(),
        depth_scanner=FakeDepthScanner(),
    )

    with pytest.raises(ValueError, match="exchange_id is required"):
        scanner.scan_route(
            exchange_id="",
            route={"route_id": "ROUTE-004", "legs": []},
            starting_value=100.0,
            max_slippage_percent=0.5,
        )
