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


import pytest


@pytest.mark.parametrize(
    "field",
    [
        "profit_percent",
        "net_profit",
    ],
)
def test_executable_opportunity_requires_ranking_economic_fields(
    field,
):
    opportunity = {
        "id": "route-a",
        "executable": True,
        "profit_percent": 2.5,
        "net_profit": 25.0,
    }
    del opportunity[field]

    with pytest.raises(
        ValueError,
        match=rf"{field} is required",
    ):
        OpportunityRanking.rank([opportunity])


@pytest.mark.parametrize(
    "field",
    [
        "profit_percent",
        "net_profit",
    ],
)
@pytest.mark.parametrize(
    "value",
    [
        None,
        "not-a-number",
        float("nan"),
        float("inf"),
        float("-inf"),
        True,
        False,
    ],
)
def test_executable_opportunity_rejects_invalid_ranking_numeric_values(
    field,
    value,
):
    opportunity = {
        "id": "route-a",
        "executable": True,
        "profit_percent": 2.5,
        "net_profit": 25.0,
    }
    opportunity[field] = value

    with pytest.raises(
        ValueError,
        match=rf"{field} must be a finite number",
    ):
        OpportunityRanking.rank([opportunity])


def test_numeric_string_ranking_values_are_supported():
    opportunities = [
        {
            "id": "route-a",
            "executable": True,
            "profit_percent": "2.5",
            "net_profit": "25.0",
        },
        {
            "id": "route-b",
            "executable": True,
            "profit_percent": "4.0",
            "net_profit": "40.0",
        },
    ]

    ranked = OpportunityRanking.rank(opportunities)

    assert [item["id"] for item in ranked] == [
        "route-b",
        "route-a",
    ]


def test_negative_and_zero_ranking_values_remain_valid():
    opportunities = [
        {
            "id": "loss",
            "executable": True,
            "profit_percent": -1.0,
            "net_profit": -10.0,
        },
        {
            "id": "breakeven",
            "executable": True,
            "profit_percent": 0.0,
            "net_profit": 0.0,
        },
    ]

    ranked = OpportunityRanking.rank(opportunities)

    assert [item["id"] for item in ranked] == [
        "breakeven",
        "loss",
    ]


def test_non_executable_opportunity_does_not_require_ranking_economics():
    opportunities = [
        {
            "id": "rejected-route",
            "executable": False,
        },
        {
            "id": "route-a",
            "executable": True,
            "profit_percent": 2.0,
            "net_profit": 20.0,
        },
    ]

    ranked = OpportunityRanking.rank(opportunities)

    assert [item["id"] for item in ranked] == [
        "route-a",
    ]
