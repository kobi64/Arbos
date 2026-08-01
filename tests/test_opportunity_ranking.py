from exchanges.opportunity_ranking import OpportunityRanking


def test_ranks_opportunities_by_profit_percent():
    opportunities = [
        {
            "id": "route-a",
            "executable": True,
            "profit_percent": 2.5,
            "net_profit": 25.0,
        },
        {
            "id": "route-b",
            "executable": True,
            "profit_percent": 4.0,
            "net_profit": 40.0,
        },
        {
            "id": "route-c",
            "executable": True,
            "profit_percent": 3.0,
            "net_profit": 30.0,
        },
    ]

    ranked = OpportunityRanking.rank(opportunities)

    assert [item["id"] for item in ranked] == [
        "route-b",
        "route-c",
        "route-a",
    ]


def test_uses_net_profit_as_tie_breaker():
    opportunities = [
        {
            "id": "route-a",
            "executable": True,
            "profit_percent": 3.0,
            "net_profit": 30.0,
        },
        {
            "id": "route-b",
            "executable": True,
            "profit_percent": 3.0,
            "net_profit": 45.0,
        },
    ]

    ranked = OpportunityRanking.rank(opportunities)

    assert [item["id"] for item in ranked] == [
        "route-b",
        "route-a",
    ]


def test_filters_non_executable_opportunities():
    opportunities = [
        {
            "id": "route-a",
            "executable": False,
            "profit_percent": 10.0,
            "net_profit": 100.0,
        },
        {
            "id": "route-b",
            "executable": True,
            "profit_percent": 2.0,
            "net_profit": 20.0,
        },
    ]

    ranked = OpportunityRanking.rank(opportunities)

    assert len(ranked) == 1
    assert ranked[0]["id"] == "route-b"


def test_returns_empty_list_when_no_opportunities():
    ranked = OpportunityRanking.rank([])

    assert ranked == []


def test_returns_empty_list_when_none_are_executable():
    opportunities = [
        {
            "id": "route-a",
            "executable": False,
            "profit_percent": 5.0,
            "net_profit": 50.0,
        }
    ]

    ranked = OpportunityRanking.rank(opportunities)

    assert ranked == []


def test_does_not_mutate_original_list():
    opportunities = [
        {
            "id": "route-a",
            "executable": True,
            "profit_percent": 2.0,
            "net_profit": 20.0,
        },
        {
            "id": "route-b",
            "executable": True,
            "profit_percent": 4.0,
            "net_profit": 40.0,
        },
    ]

    original = list(opportunities)

    OpportunityRanking.rank(opportunities)

    assert opportunities == original
