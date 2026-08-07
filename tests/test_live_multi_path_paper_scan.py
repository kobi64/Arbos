from core.live_multi_path_paper_scan import (
    LiveMultiPathPaperScan,
)


class FakeInternalScanner:
    def scan(self, **kwargs):
        return {
            "best_route": {
                "route_id": "INTERNAL-ETH",
                "bridge_asset": "ETH",
                "filled": True,
                "net_final_value": 102.1,
                "net_profit": 2.1,
                "net_profit_percent": 2.1,
            },
            "ranked_routes": [
                {
                    "route_id": "INTERNAL-ETH",
                    "bridge_asset": "ETH",
                    "filled": True,
                    "net_final_value": 102.1,
                    "net_profit": 2.1,
                    "net_profit_percent": 2.1,
                },
            ],
        }


class FakeIntegrationCoordinator:
    def evaluate(
        self,
        internal_routes,
        cross_exchange_generate_kwargs,
        starting_usdt_value,
        destination_fee_rate,
        max_slippage_percent,
    ):
        return {
            "best_route": {
                "route_id": "DIRECT-COINX",
                "route_type": "direct_cross_exchange",
                "executable": True,
                "net_final_value": 103.2,
                "net_profit": 3.2,
                "net_profit_percent": 3.2,
            },
            "ranked_routes": [
                {
                    "route_id": "DIRECT-COINX",
                    "route_type": "direct_cross_exchange",
                    "executable": True,
                    "net_final_value": 103.2,
                    "net_profit": 3.2,
                    "net_profit_percent": 3.2,
                },
                {
                    "route_id": "INTERNAL-ETH",
                    "route_type": "internal_triangle",
                    "executable": True,
                    "net_final_value": 102.1,
                    "net_profit": 2.1,
                    "net_profit_percent": 2.1,
                },
            ],
            "executable_count": 2,
            "paper_only": True,
            "live_order_submitted": False,
        }


def test_runs_internal_and_cross_exchange_paths_and_returns_best():
    scanner = LiveMultiPathPaperScan(
        internal_scanner=FakeInternalScanner(),
        integration_coordinator=FakeIntegrationCoordinator(),
    )

    result = scanner.scan(
        markets={"dummy": {}},
        quote_asset="USDT",
        coin_asset="COINX",
        starting_value=100.0,
        fee_rate=0.001,
        destination_fee_rate=0.001,
        max_slippage_percent=0.5,
        cross_exchange_generate_kwargs={},
    )

    assert result["best_route"]["route_id"] == "DIRECT-COINX"
    assert result["paper_only"] is True
    assert result["live_order_submitted"] is False
