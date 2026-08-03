import pytest

from exchanges.safe_live_paper_replay_engine import (
    SafeLivePaperReplayEngine,
)


@pytest.fixture
def engine():
    return SafeLivePaperReplayEngine()


def valid_audit_record():
    return {
        "record_id": "AUDIT-084",
        "opportunity_id": "OPP-084",
        "readiness": {
            "ready": True,
        },
        "approval": {
            "approved": True,
        },
        "execution": {
            "status": "COMPLETED",
        },
        "pnl": {
            "profit_percent": 4.0,
        },
    }


def test_replay_reconstructs_audit_decision(engine):
    result = engine.replay(
        valid_audit_record()
    )

    assert result["replayed"] is True
    assert result["opportunity_id"] == "OPP-084"
    assert result["execution"]["status"] == "COMPLETED"


def test_replay_requires_record_id(engine):
    record = valid_audit_record()
    del record["record_id"]

    with pytest.raises(
        ValueError,
        match="record_id is required",
    ):
        engine.replay(record)


def test_replay_requires_opportunity_id(engine):
    record = valid_audit_record()
    del record["opportunity_id"]

    with pytest.raises(
        ValueError,
        match="opportunity_id is required",
    ):
        engine.replay(record)


def test_history_stores_replays(engine):
    engine.replay(
        valid_audit_record()
    )

    assert len(engine.history()) == 1
