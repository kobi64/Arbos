import pytest

from exchanges.safe_live_paper_performance_analyzer import (
    SafeLivePaperPerformanceAnalyzer,
)


@pytest.fixture
def analyzer():
    return SafeLivePaperPerformanceAnalyzer()


def replay_records():
    return [
        {
            "execution": {
                "status": "COMPLETED",
            },
            "pnl": {
                "profit": 25.0,
            },
        },
        {
            "execution": {
                "status": "COMPLETED",
            },
            "pnl": {
                "profit": 15.0,
            },
        },
        {
            "execution": {
                "status": "FAILED",
            },
            "pnl": {
                "profit": -5.0,
            },
        },
        {
            "execution": {
                "status": "REJECTED",
            },
            "pnl": {
                "profit": 0,
            },
        },
    ]


def test_analyzer_calculates_performance(analyzer):
    result = analyzer.analyze(
        replay_records()
    )

    assert result["total_records"] == 4
    assert result["completed"] == 2
    assert result["failed"] == 1
    assert result["rejected"] == 1
    assert result["total_profit"] == 35.0
    assert result["average_profit"] == 17.5


def test_analyzer_requires_records(analyzer):
    with pytest.raises(
        ValueError,
        match="replay_records are required",
    ):
        analyzer.analyze(None)


def test_analyzer_requires_list(analyzer):
    with pytest.raises(
        ValueError,
        match="replay_records must be a list",
    ):
        analyzer.analyze({})


def test_history_stores_analysis(analyzer):
    analyzer.analyze(
        replay_records()
    )

    assert len(analyzer.history()) == 1
