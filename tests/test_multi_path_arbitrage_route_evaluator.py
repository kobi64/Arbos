from core.multi_path_arbitrage_route_evaluator import (
    MultiPathArbitrageRouteEvaluator,
)


def sample_candidates():
    return [
        {
            "route_id": "INTERNAL-ETH",
            "route_type": "internal_triangle",
            "executable": True,
            "net_final_value": 102.10,
            "net_profit": 2.10,
            "net_profit_percent": 2.10,
        },
        {
            "route_id": "DIRECT-COINX",
            "route_type": "direct_cross_exchange",
            "executable": True,
            "net_final_value": 103.20,
            "net_profit": 3.20,
            "net_profit_percent": 3.20,
        },
        {
            "route_id": "BRIDGE-BTC",
            "route_type": "bridge_cross_exchange",
            "executable": True,
            "net_final_value": 102.70,
            "net_profit": 2.70,
            "net_profit_percent": 2.70,
        },
    ]


def test_selects_best_executable_route_across_all_route_families():
    evaluator = MultiPathArbitrageRouteEvaluator()

    result = evaluator.evaluate(
        sample_candidates()
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


def test_excludes_non_executable_routes_before_ranking():
    candidates = sample_candidates()

    candidates.append({
        "route_id": "IMPOSSIBLE-SOL",
        "route_type": "bridge_cross_exchange",
        "executable": False,
        "net_final_value": 110.0,
        "net_profit": 10.0,
        "net_profit_percent": 10.0,
        "reason": "withdrawal_unavailable",
    })

    evaluator = MultiPathArbitrageRouteEvaluator()

    result = evaluator.evaluate(candidates)

    assert result["best_route"]["route_id"] == "DIRECT-COINX"

    assert all(
        route["executable"] is True
        for route in result["ranked_routes"]
    )


def test_returns_no_best_route_when_none_are_executable():
    evaluator = MultiPathArbitrageRouteEvaluator()

    result = evaluator.evaluate([
        {
            "route_id": "FAILED-1",
            "route_type": "internal_triangle",
            "executable": False,
            "reason": "insufficient_liquidity",
        },
        {
            "route_id": "FAILED-2",
            "route_type": "direct_cross_exchange",
            "executable": False,
            "reason": "withdrawal_unavailable",
        },
    ])

    assert result["best_route"] is None
    assert result["ranked_routes"] == []


def test_separates_internal_and_cross_exchange_rankings():
    evaluator = MultiPathArbitrageRouteEvaluator()

    candidates = [
        {
            "route_id": "INTERNAL-1",
            "route_type": "internal_triangle",
            "executable": True,
            "net_profit": 1.5,
            "net_profit_percent": 1.5,
        },
        {
            "route_id": "DIRECT-1",
            "route_type": "direct_cross_exchange",
            "executable": True,
            "net_profit": 2.0,
            "net_profit_percent": 2.0,
        },
        {
            "route_id": "BRIDGE-1",
            "route_type": "bridge_cross_exchange",
            "executable": True,
            "net_profit": 1.0,
            "net_profit_percent": 1.0,
        },
    ]

    result = evaluator.evaluate(candidates)

    assert result["best_route"]["route_id"] == "DIRECT-1"

    assert result["best_internal"]["route_id"] == "INTERNAL-1"

    assert (
        result["best_cross_exchange"]["route_id"]
        == "DIRECT-1"
    )

    assert [
        route["route_id"]
        for route in result["ranked_internal"]
    ] == [
        "INTERNAL-1",
    ]

    assert [
        route["route_id"]
        for route in result["ranked_cross_exchange"]
    ] == [
        "DIRECT-1",
        "BRIDGE-1",
    ]
