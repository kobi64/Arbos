import pytest

from exchanges.safe_live_paper_audit_recorder import (
    SafeLivePaperAuditRecorder,
)


@pytest.fixture
def recorder():
    return SafeLivePaperAuditRecorder()


def test_record_decision_creates_audit_record(recorder):
    result = recorder.record_decision(
        opportunity_id="OPP-083",
        readiness={
            "ready": True,
            "reason": "ready_for_safe_live_paper_execution",
        },
        approval={
            "approved": True,
        },
        execution={
            "status": "COMPLETED",
        },
        pnl={
            "profit_percent": 3.5,
        },
    )

    assert result["opportunity_id"] == "OPP-083"
    assert result["execution"]["status"] == "COMPLETED"


def test_record_contains_unique_id(recorder):
    result = recorder.record_decision(
        opportunity_id="OPP-083",
        readiness={},
        approval={},
        execution={},
        pnl={},
    )

    assert "record_id" in result
    assert result["record_id"]


def test_history_stores_records(recorder):
    recorder.record_decision(
        opportunity_id="OPP-083",
        readiness={},
        approval={},
        execution={},
        pnl={},
    )

    assert len(recorder.history()) == 1


def test_missing_opportunity_is_rejected(recorder):
    with pytest.raises(ValueError, match="opportunity_id is required"):
        recorder.record_decision(
            opportunity_id=None,
            readiness={},
            approval={},
            execution={},
            pnl={},
        )
