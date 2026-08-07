from core.internal_multi_bridge_route_ranker import (
    InternalMultiBridgeRouteRanker,
)


def sample_results():
    return [
        {
            "route_id": "USDT-COINX-BTC-USDT",
            "bridge_asset": "BTC",
            "filled": True,
            "net_final_value": 101.20,
            "net_profit": 1.20,
            "net_profit_percent": 1.20,
        },
        {
            "route_id": "USDT-COINX-ETH-USDT",
            "bridge_asset": "ETH",
            "filled": True,
            "net_final_value": 102.40,
            "net_profit": 2.40,
            "net_profit_percent": 2.40,
        },
        {
            "route_id": "USDT-COINX-SOL-USDT",
            "bridge_asset": "SOL",
            "filled": True,
            "net_final_value": 101.80,
            "net_profit": 1.80,
            "net_profit_percent": 1.80,
        },
    ]


def test_ranks_filled_internal_routes_by_net_profit_percent():
    ranker = InternalMultiBridgeRouteRanker()

    ranked = ranker.rank(sample_results())

    assert [
        result["bridge_asset"]
        for result in ranked
    ] == [
        "ETH",
        "SOL",
        "BTC",
    ]


def test_preserves_original_route_result_fields():
    ranker = InternalMultiBridgeRouteRanker()

    ranked = ranker.rank(sample_results())

    assert ranked[0]["route_id"] == "USDT-COINX-ETH-USDT"
    assert ranked[0]["net_final_value"] == 102.40


def test_excludes_routes_that_could_not_be_filled():
    results = sample_results()

    results.append({
        "route_id": "USDT-COINX-XLM-USDT",
        "bridge_asset": "XLM",
        "filled": False,
        "reason": "insufficient_liquidity",
    })

    ranker = InternalMultiBridgeRouteRanker()

    ranked = ranker.rank(results)

    assert len(ranked) == 3
    assert all(result["filled"] is True for result in ranked)
