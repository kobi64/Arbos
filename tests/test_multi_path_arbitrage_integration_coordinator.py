from core.multi_path_arbitrage_integration_coordinator import (
    MultiPathArbitrageIntegrationCoordinator,
)


class FakeCrossExchangeGenerator:
    def generate(self, **kwargs):
        return [
            {
                "route_id": "DIRECT-COINX",
                "route_type": "direct_cross_exchange",
                "transfer_asset": "COINX",
                "transfer_amount": 98.0,
                "executable": True,
            },
            {
                "route_id": "BRIDGE-BTC",
                "route_type": "bridge_cross_exchange",
                "transfer_asset": "BTC",
                "transfer_amount": 0.0024,
                "executable": True,
            },
        ]


class FakeCrossExchangeValuation:
    def evaluate(
        self,
        candidate,
        starting_usdt_value,
        destination_fee_rate,
        max_slippage_percent,
    ):
        values = {
            "DIRECT-COINX": 103.2,
            "BRIDGE-BTC": 102.7,
        }

        final_value = values[candidate["route_id"]]
        profit = final_value - starting_usdt_value

        return {
            **candidate,
            "executable": True,
            "net_final_value": final_value,
            "net_profit": profit,
            "net_profit_percent": (
                profit / starting_usdt_value
            ) * 100.0,
        }


class FakeEvaluator:
    def evaluate(self, candidates):
        executable = [
            candidate
            for candidate in candidates
            if candidate.get("executable") is True
        ]

        ranked = sorted(
            executable,
            key=lambda candidate: candidate["net_profit_percent"],
            reverse=True,
        )

        return {
            "best_route": ranked[0] if ranked else None,
            "ranked_routes": ranked,
            "executable_count": len(ranked),
        }


def test_combines_internal_and_cross_exchange_routes_and_selects_best():
    coordinator = MultiPathArbitrageIntegrationCoordinator(
        cross_exchange_generator=FakeCrossExchangeGenerator(),
        cross_exchange_valuation=FakeCrossExchangeValuation(),
        evaluator=FakeEvaluator(),
    )

    internal_routes = [
        {
            "route_id": "INTERNAL-ETH",
            "route_type": "internal_triangle",
            "filled": True,
            "net_final_value": 102.1,
            "net_profit": 2.1,
            "net_profit_percent": 2.1,
        },
    ]

    result = coordinator.evaluate(
        internal_routes=internal_routes,
        cross_exchange_generate_kwargs={},
        starting_usdt_value=100.0,
        destination_fee_rate=0.001,
        max_slippage_percent=0.5,
    )

    assert result["best_route"]["route_id"] == "DIRECT-COINX"

    assert [
        route["route_id"]
        for route in result["ranked_routes"]
    ] == [
        "DIRECT-COINX",
        "BRIDGE-BTC",
        "INTERNAL-ETH",
    ]


def test_excludes_unfilled_internal_routes_from_final_competition():
    coordinator = MultiPathArbitrageIntegrationCoordinator(
        cross_exchange_generator=FakeCrossExchangeGenerator(),
        cross_exchange_valuation=FakeCrossExchangeValuation(),
        evaluator=FakeEvaluator(),
    )

    internal_routes = [
        {
            "route_id": "INTERNAL-FAILED",
            "route_type": "internal_triangle",
            "filled": False,
            "reason": "insufficient_liquidity",
        },
    ]

    result = coordinator.evaluate(
        internal_routes=internal_routes,
        cross_exchange_generate_kwargs={},
        starting_usdt_value=100.0,
        destination_fee_rate=0.001,
        max_slippage_percent=0.5,
    )

    assert result["best_route"]["route_id"] == "DIRECT-COINX"
    assert all(
        route["route_id"] != "INTERNAL-FAILED"
        for route in result["ranked_routes"]
    )
