import pytest

from core.auto_discovered_multi_exchange_scanner import (
    AutoDiscoveredMultiExchangeScanner,
)


class FakeDiscovery:
    def discover(self, markets, quote_asset, bridge_asset):
        routes = markets.get("routes", [])
        return [dict(route) for route in routes]


class FakeRouteScanner:
    def scan_route(
        self,
        exchange_id,
        route,
        starting_value,
        max_slippage_percent,
        fee_type="taker",
    ):
        profits = {
            ("kraken", "R1"): -0.8,
            ("kraken", "R2"): 0.2,
            ("kucoin", "R3"): 0.5,
        }

        return {
            "exchange_id": exchange_id,
            "route_id": route["route_id"],
            "filled": True,
            "net_profit_percent": profits[
                (exchange_id, route["route_id"])
            ],
            "paper_only": True,
            "live_order_submitted": False,
        }


def test_discovers_scans_and_ranks_routes_across_exchanges():
    scanner = AutoDiscoveredMultiExchangeScanner(
        discovery=FakeDiscovery(),
        route_scanner=FakeRouteScanner(),
    )

    exchange_markets = {
        "kraken": {
            "routes": [
                {"route_id": "R1", "legs": []},
                {"route_id": "R2", "legs": []},
            ],
        },
        "kucoin": {
            "routes": [
                {"route_id": "R3", "legs": []},
            ],
        },
    }

    results = scanner.scan(
        exchange_markets=exchange_markets,
        quote_asset="USDT",
        bridge_asset="BTC",
        starting_value=100.0,
        max_slippage_percent=0.5,
    )

    assert len(results) == 3
    assert results[0]["exchange_id"] == "kucoin"
    assert results[0]["route_id"] == "R3"
    assert results[1]["route_id"] == "R2"
    assert results[2]["route_id"] == "R1"


def test_accepts_arbitrary_number_of_venues():
    class ManyVenueRouteScanner:
        def scan_route(
            self,
            exchange_id,
            route,
            starting_value,
            max_slippage_percent,
            fee_type="taker",
        ):
            return {
                "exchange_id": exchange_id,
                "route_id": route["route_id"],
                "filled": True,
                "net_profit_percent": float(route["score"]),
                "paper_only": True,
                "live_order_submitted": False,
            }

    scanner = AutoDiscoveredMultiExchangeScanner(
        discovery=FakeDiscovery(),
        route_scanner=ManyVenueRouteScanner(),
    )

    exchange_markets = {
        "venue1": {"routes": [{"route_id": "A", "score": -0.3, "legs": []}]},
        "venue2": {"routes": [{"route_id": "B", "score": 0.1, "legs": []}]},
        "venue3": {"routes": [{"route_id": "C", "score": 0.4, "legs": []}]},
        "venue4": {"routes": [{"route_id": "D", "score": -0.1, "legs": []}]},
        "venue5": {"routes": [{"route_id": "E", "score": 0.2, "legs": []}]},
    }

    results = scanner.scan(
        exchange_markets=exchange_markets,
        quote_asset="USDT",
        bridge_asset="BTC",
        starting_value=100.0,
        max_slippage_percent=0.5,
    )

    assert len(results) == 5
    assert results[0]["exchange_id"] == "venue3"
    assert results[-1]["exchange_id"] == "venue1"


def test_one_venue_failure_does_not_stop_global_scan():
    class FailingDiscovery(FakeDiscovery):
        def discover(self, markets, quote_asset, bridge_asset):
            if markets.get("fail"):
                raise RuntimeError("venue discovery failed")
            return super().discover(markets, quote_asset, bridge_asset)

    scanner = AutoDiscoveredMultiExchangeScanner(
        discovery=FailingDiscovery(),
        route_scanner=FakeRouteScanner(),
    )

    exchange_markets = {
        "kraken": {
            "routes": [{"route_id": "R1", "legs": []}],
        },
        "broken": {"fail": True},
        "kucoin": {
            "routes": [{"route_id": "R3", "legs": []}],
        },
    }

    results = scanner.scan(
        exchange_markets=exchange_markets,
        quote_asset="USDT",
        bridge_asset="BTC",
        starting_value=100.0,
        max_slippage_percent=0.5,
    )

    exchange_ids = {result["exchange_id"] for result in results}

    assert "kraken" in exchange_ids
    assert "kucoin" in exchange_ids
    assert "broken" in exchange_ids

    failed = next(
        result for result in results
        if result["exchange_id"] == "broken"
    )
    assert failed["filled"] is False
    assert failed["reason"] == "venue_discovery_failed"
