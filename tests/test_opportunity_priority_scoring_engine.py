import pytest

from core.opportunity_priority_scoring_engine import (
    OpportunityPriorityScoringEngine,
)


@pytest.fixture
def engine():
    return OpportunityPriorityScoringEngine()


def test_scores_balanced_opportunity(engine):
    result = engine.score(
        net_profit_percent=1.5,
        liquidity_score=80.0,
        reliability_score=90.0,
        age_seconds=5.0,
        route_complexity=2,
    )

    assert result["score"] > 0
    assert result["score"] <= 100
    assert result["priority"] == result["score"]


def test_higher_quality_opportunity_scores_higher(engine):
    strong = engine.score(
        net_profit_percent=2.0,
        liquidity_score=90.0,
        reliability_score=95.0,
        age_seconds=2.0,
        route_complexity=2,
    )

    weak = engine.score(
        net_profit_percent=0.2,
        liquidity_score=30.0,
        reliability_score=50.0,
        age_seconds=60.0,
        route_complexity=5,
    )

    assert strong["score"] > weak["score"]


def test_age_and_complexity_reduce_score(engine):
    fresh_simple = engine.score(
        net_profit_percent=1.0,
        liquidity_score=70.0,
        reliability_score=80.0,
        age_seconds=1.0,
        route_complexity=2,
    )

    stale_complex = engine.score(
        net_profit_percent=1.0,
        liquidity_score=70.0,
        reliability_score=80.0,
        age_seconds=120.0,
        route_complexity=6,
    )

    assert fresh_simple["score"] > stale_complex["score"]


def test_rejects_negative_age(engine):
    with pytest.raises(ValueError, match="age_seconds cannot be negative"):
        engine.score(
            net_profit_percent=1.0,
            liquidity_score=70.0,
            reliability_score=80.0,
            age_seconds=-1.0,
            route_complexity=2,
        )


def test_rejects_non_positive_route_complexity(engine):
    with pytest.raises(ValueError, match="route_complexity must be positive"):
        engine.score(
            net_profit_percent=1.0,
            liquidity_score=70.0,
            reliability_score=80.0,
            age_seconds=1.0,
            route_complexity=0,
        )
