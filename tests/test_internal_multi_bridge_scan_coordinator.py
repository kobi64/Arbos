from core.internal_multi_bridge_scan_coordinator import (
    InternalMultiBridgeScanCoordinator,
)


class FakeDiscovery:
    def discover(
        self,
        markets,
        quote_asset,
        coin_asset,
    ):
        return [
            {
                "route_id": "USDT-COINX-BTC-USDT",
                "bridge_asset": "BTC",
                "legs": [],
            },
            {
                "route_id": "USDT-COINX-ETH-USDT",
                "bridge_asset": "ETH",
                "legs": [],
            },
            {
                "route_id": "USDT-COINX-SOL-USDT",
                "bridge_asset": "SOL",
                "legs": [],
            },
        ]


class FakeRouteScanner:
    def __init__(self):
        self.calls = []

    def scan_route(
        self,
        route,
        starting_value,
        fee_rate,
        max_slippage_percent,
    ):
        self.calls.append(route["route_id"])

        returns = {
            "BTC": 1.20,
            "ETH": 2.40,
            "SOL": 1.80,
        }

        profit_percent = returns[route["bridge_asset"]]

        return {
            "route_id": route["route_id"],
            "bridge_asset": route["bridge_asset"],
            "filled": True,
            "net_final_value": starting_value * (
                1 + profit_percent / 100.0
            ),
            "net_profit": starting_value * (
                profit_percent / 100.0
            ),
            "net_profit_percent": profit_percent,
        }


class FakeRanker:
    def rank(self, results):
        return sorted(
            results,
            key=lambda result: result["net_profit_percent"],
            reverse=True,
        )


def test_discovers_values_and_ranks_all_internal_bridge_routes():
    scanner = FakeRouteScanner()

    coordinator = InternalMultiBridgeScanCoordinator(
        discovery=FakeDiscovery(),
        route_scanner=scanner,
        ranker=FakeRanker(),
    )

    result = coordinator.scan(
        markets={"dummy": {}},
        quote_asset="USDT",
        coin_asset="COINX",
        starting_value=100.0,
        fee_rate=0.001,
        max_slippage_percent=0.5,
    )

    assert scanner.calls == [
        "USDT-COINX-BTC-USDT",
        "USDT-COINX-ETH-USDT",
        "USDT-COINX-SOL-USDT",
    ]

    assert result["best_route"]["bridge_asset"] == "ETH"

    assert [
        route["bridge_asset"]
        for route in result["ranked_routes"]
    ] == [
        "ETH",
        "SOL",
        "BTC",
    ]


def test_returns_no_best_route_when_nothing_is_filled():
    class UnfilledScanner:
        def scan_route(
            self,
            route,
            starting_value,
            fee_rate,
            max_slippage_percent,
        ):
            return {
                "route_id": route["route_id"],
                "bridge_asset": route["bridge_asset"],
                "filled": False,
                "reason": "insufficient_liquidity",
            }

    coordinator = InternalMultiBridgeScanCoordinator(
        discovery=FakeDiscovery(),
        route_scanner=UnfilledScanner(),
        ranker=FakeRanker(),
    )

    result = coordinator.scan(
        markets={"dummy": {}},
        quote_asset="USDT",
        coin_asset="COINX",
        starting_value=100.0,
        fee_rate=0.001,
        max_slippage_percent=0.5,
    )

    assert result["best_route"] is None
    assert result["ranked_routes"] == []
