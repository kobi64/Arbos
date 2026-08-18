import pytest

from core.live_opportunity_intake_service import (
    LiveOpportunityIntakeService,
)


class FakeScheduler:
    def __init__(self):
        self.enqueued = []

    def enqueue(self, opportunity):
        self.enqueued.append(dict(opportunity))
        return {
            "queued": True,
            "opportunity_id": opportunity["opportunity_id"],
            "priority": opportunity.get("priority", 0.0),
        }


@pytest.fixture
def intake():
    return LiveOpportunityIntakeService(FakeScheduler())


def test_accepts_and_forwards_valid_opportunity(intake):
    result = intake.submit({
        "opportunity_id": "OPP-001",
        "priority": 5,
        "route": {"route_id": "ROUTE-001"},
    })

    assert result["accepted"] is True
    assert result["queued"] is True
    assert result["opportunity_id"] == "OPP-001"


def test_rejects_missing_opportunity_id(intake):
    with pytest.raises(ValueError, match="opportunity_id is required"):
        intake.submit({
            "priority": 1,
            "route": {"route_id": "ROUTE-001"},
        })


def test_rejects_missing_route(intake):
    with pytest.raises(ValueError, match="route is required"):
        intake.submit({
            "opportunity_id": "OPP-002",
            "priority": 1,
        })


def test_rejects_duplicate_opportunity_id(intake):
    opportunity = {
        "opportunity_id": "OPP-003",
        "priority": 2,
        "route": {"route_id": "ROUTE-003"},
    }

    intake.submit(opportunity)

    with pytest.raises(ValueError, match="opportunity_id already received"):
        intake.submit(opportunity)


def test_reports_intake_statistics(intake):
    intake.submit({
        "opportunity_id": "OPP-004",
        "priority": 3,
        "route": {"route_id": "ROUTE-004"},
    })

    stats = intake.statistics()

    assert stats["received"] == 1
    assert stats["accepted"] == 1
    assert stats["rejected"] == 0


def test_missing_scheduler_is_rejected():
    with pytest.raises(ValueError, match="scheduler is required"):
        LiveOpportunityIntakeService(None)


def test_rejected_submission_updates_statistics(intake):
    with pytest.raises(ValueError, match="route is required"):
        intake.submit({
            "opportunity_id": "OPP-005",
            "priority": 1,
        })

    stats = intake.statistics()
    assert stats["received"] == 1
    assert stats["accepted"] == 0
    assert stats["rejected"] == 1


class SchedulerWithResult:
    def __init__(self, result):
        self.result = result

    def enqueue(self, opportunity):
        return dict(self.result)


def valid_intake_opportunity():
    return {
        "opportunity_id": "OPP-CONTRACT",
        "priority": 5,
        "route": {"route_id": "ROUTE-CONTRACT"},
    }


def test_intake_preserves_scheduler_canonical_priority():
    intake = LiveOpportunityIntakeService(
        SchedulerWithResult(
            {
                "queued": True,
                "opportunity_id": "OPP-CONTRACT",
                "priority": 5.5,
            }
        )
    )

    result = intake.submit(valid_intake_opportunity())

    assert result["priority"] == 5.5


def test_intake_requires_scheduler_priority_result():
    intake = LiveOpportunityIntakeService(
        SchedulerWithResult(
            {
                "queued": True,
                "opportunity_id": "OPP-CONTRACT",
            }
        )
    )

    with pytest.raises(
        ValueError,
        match="scheduler priority is required",
    ):
        intake.submit(valid_intake_opportunity())


@pytest.mark.parametrize(
    "priority",
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
def test_intake_rejects_invalid_scheduler_priority(
    priority,
):
    intake = LiveOpportunityIntakeService(
        SchedulerWithResult(
            {
                "queued": True,
                "opportunity_id": "OPP-CONTRACT",
                "priority": priority,
            }
        )
    )

    with pytest.raises(
        ValueError,
        match="scheduler priority must be a finite number",
    ):
        intake.submit(valid_intake_opportunity())


def test_intake_normalizes_scheduler_numeric_string_priority():
    intake = LiveOpportunityIntakeService(
        SchedulerWithResult(
            {
                "queued": True,
                "opportunity_id": "OPP-CONTRACT",
                "priority": "5.5",
            }
        )
    )

    result = intake.submit(valid_intake_opportunity())

    assert result["priority"] == 5.5
    assert isinstance(result["priority"], float)
