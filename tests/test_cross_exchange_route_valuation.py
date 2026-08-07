import pytest

from core.cross_exchange_route_valuation import (
    CrossExchangeRouteValuation,
)


class FakeDestinationScanner:
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

        symbol = route["legs"][0]["symbol"]

        final_values = {
            "COINX/USDT": 104.0,
            "BTC/USDT": 103.0,
        }

        return {
            "route_id": route["route_id"],
            "filled": True,
            "net_final_value": final_values[symbol],
            "max_leg_slippage_percent": 0.1,
            "paper_only": True,
            "live_order_submitted": False,
        }


def test_values_direct_cross_exchange_candidate_to_final_usdt():
    valuation = CrossExchangeRouteValuation(
        destination_scanner=FakeDestinationScanner(),
    )

    candidate = {
        "route_id": "DIRECT-A-COINX-B",
        "route_type": "direct_cross_exchange",
        "transfer_asset": "COINX",
        "transfer_amount": 98.0,
        "executable": True,
    }

    result = valuation.evaluate(
        candidate=candidate,
        starting_usdt_value=100.0,
        destination_fee_rate=0.001,
        max_slippage_percent=0.5,
    )

    assert result["executable"] is True
    assert result["net_final_value"] == 104.0
    assert result["net_profit"] == 4.0
    assert result["net_profit_percent"] == 4.0


def test_values_bridge_candidate_using_bridge_usdt_market():
    scanner = FakeDestinationScanner()

    valuation = CrossExchangeRouteValuation(
        destination_scanner=scanner,
    )

    candidate = {
        "route_id": "BRIDGE-A-COINX-BTC-B",
        "route_type": "bridge_cross_exchange",
        "transfer_asset": "BTC",
        "transfer_amount": 0.0024,
        "executable": True,
    }

    result = valuation.evaluate(
        candidate=candidate,
        starting_usdt_value=100.0,
        destination_fee_rate=0.001,
        max_slippage_percent=0.5,
    )

    assert result["net_final_value"] == 103.0
    assert result["net_profit_percent"] == 3.0

    leg = scanner.calls[0]["route"]["legs"][0]

    assert leg == {
        "symbol": "BTC/USDT",
        "side": "sell",
    }


def test_rejects_candidate_that_is_already_non_executable():
    valuation = CrossExchangeRouteValuation(
        destination_scanner=FakeDestinationScanner(),
    )

    candidate = {
        "route_id": "FAILED",
        "route_type": "direct_cross_exchange",
        "transfer_asset": "COINX",
        "transfer_amount": 0.0,
        "executable": False,
        "reason": "no_compatible_network",
    }

    result = valuation.evaluate(
        candidate=candidate,
        starting_usdt_value=100.0,
        destination_fee_rate=0.001,
        max_slippage_percent=0.5,
    )

    assert result["executable"] is False
    assert result["reason"] == "no_compatible_network"
