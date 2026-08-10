from core.multi_path_arbitrage_route_evaluator import (
    MultiPathArbitrageRouteEvaluator,
)


def test_rejected_cross_exchange_route_is_preserved():
    evaluator = MultiPathArbitrageRouteEvaluator()

    rejected = {
        "route_id": "DIRECT-kucoin-COTI-digifinex",
        "route_type": "direct_cross_exchange",
        "coin_asset": "COTI",
        "transfer_asset": "COTI",
        "network": "COTI",
        "network_identity": "UNVERIFIED",
        "executable": False,
        "reason": "network_identity_unverified",
    }

    result = evaluator.evaluate([
        rejected,
    ])

    assert result["ranked_routes"] == []
    assert result["executable_count"] == 0

    assert result["rejected_count"] == 1
    assert result["rejected_routes"] == [
        rejected
    ]
    assert result["rejected_cross_exchange"] == [
        rejected
    ]


def test_rejected_route_never_enters_executable_ranking():
    evaluator = MultiPathArbitrageRouteEvaluator()

    executable = {
        "route_id": "EXECUTABLE",
        "route_type": "direct_cross_exchange",
        "executable": True,
        "net_profit": 1.0,
        "net_profit_percent": 1.0,
    }

    rejected = {
        "route_id": "REJECTED",
        "route_type": "direct_cross_exchange",
        "executable": False,
        "reason": "network_identity_unverified",
        "net_profit": 1000.0,
        "net_profit_percent": 1000.0,
    }

    result = evaluator.evaluate([
        rejected,
        executable,
    ])

    assert result["executable_count"] == 1
    assert len(result["ranked_routes"]) == 1
    assert (
        result["ranked_routes"][0]["route_id"]
        == "EXECUTABLE"
    )

    assert result["rejected_count"] == 1
    assert (
        result["rejected_routes"][0]["route_id"]
        == "REJECTED"
    )


def test_empty_evaluation_has_empty_rejection_audit():
    result = (
        MultiPathArbitrageRouteEvaluator()
        .evaluate([])
    )

    assert result["executable_count"] == 0
    assert result["rejected_count"] == 0
    assert result["rejected_routes"] == []
    assert result["rejected_cross_exchange"] == []
