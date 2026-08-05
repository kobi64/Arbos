import pytest

from core.continuous_opportunity_scheduler import (
    ContinuousOpportunityScheduler,
)


class FakeCoordinator:
    def __init__(self):
        self.executed = []

    def execute(self, opportunity):
        self.executed.append(opportunity["opportunity_id"])
        return {
            "opportunity_id": opportunity["opportunity_id"],
            "status": "COMPLETED",
        }


@pytest.fixture
def scheduler():
    return ContinuousOpportunityScheduler(FakeCoordinator())


def test_enqueues_opportunity(scheduler):
    scheduler.enqueue({
        "opportunity_id": "OPP-001",
        "priority": 5,
    })

    assert scheduler.pending_count() == 1


def test_processes_highest_priority_first(scheduler):
    scheduler.enqueue({"opportunity_id": "OPP-LOW", "priority": 1})
    scheduler.enqueue({"opportunity_id": "OPP-HIGH", "priority": 10})

    result = scheduler.process_next()

    assert result["opportunity_id"] == "OPP-HIGH"
    assert scheduler.pending_count() == 1


def test_rejects_duplicate_opportunity_id(scheduler):
    scheduler.enqueue({"opportunity_id": "OPP-001", "priority": 1})

    with pytest.raises(ValueError, match="opportunity_id already queued"):
        scheduler.enqueue({"opportunity_id": "OPP-001", "priority": 2})


def test_process_next_returns_none_when_queue_empty(scheduler):
    assert scheduler.process_next() is None


def test_missing_opportunity_id_is_rejected(scheduler):
    with pytest.raises(ValueError, match="opportunity_id is required"):
        scheduler.enqueue({"priority": 1})
