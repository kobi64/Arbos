from exchanges.opportunity_selection import OpportunitySelection


def test_selects_highest_ranked_opportunity():
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

    selected = OpportunitySelection.select(opportunities)

    assert selected is not None
    assert selected["id"] == "route-b"


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

    selected = OpportunitySelection.select(opportunities)

    assert selected["id"] == "route-b"


def test_ignores_non_executable_opportunities():
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

    selected = OpportunitySelection.select(opportunities)

    assert selected["id"] == "route-b"


def test_returns_none_for_empty_list():
    selected = OpportunitySelection.select([])

    assert selected is None


def test_returns_none_when_none_are_executable():
    opportunities = [
        {
            "id": "route-a",
            "executable": False,
            "profit_percent": 5.0,
            "net_profit": 50.0,
        },
        {
            "id": "route-b",
            "executable": False,
            "profit_percent": 8.0,
            "net_profit": 80.0,
        },
    ]

    selected = OpportunitySelection.select(opportunities)

    assert selected is None


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

    OpportunitySelection.select(opportunities)

    assert opportunities == original
