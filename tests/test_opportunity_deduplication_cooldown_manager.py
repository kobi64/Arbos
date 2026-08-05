import pytest

from core.opportunity_deduplication_cooldown_manager import (
    OpportunityDeduplicationCooldownManager,
)


class FakeClock:
    def __init__(self):
        self.value = 1000.0

    def now(self):
        return self.value

    def advance(self, seconds):
        self.value += seconds


@pytest.fixture
def clock():
    return FakeClock()


@pytest.fixture
def manager(clock):
    return OpportunityDeduplicationCooldownManager(
        cooldown_seconds=30,
        clock=clock.now,
    )


def test_accepts_first_occurrence(manager):
    result = manager.evaluate("OPP-001")

    assert result["accepted"] is True
    assert result["reason"] is None


def test_rejects_duplicate_during_cooldown(manager):
    manager.evaluate("OPP-001")

    result = manager.evaluate("OPP-001")

    assert result["accepted"] is False
    assert result["reason"] == "cooldown_active"
    assert result["remaining_seconds"] == 30.0


def test_accepts_again_after_cooldown_expires(manager, clock):
    manager.evaluate("OPP-001")
    clock.advance(30)

    result = manager.evaluate("OPP-001")

    assert result["accepted"] is True
    assert result["reason"] is None


def test_reports_statistics(manager):
    manager.evaluate("OPP-001")
    manager.evaluate("OPP-001")
    manager.evaluate("OPP-002")

    stats = manager.statistics()

    assert stats["accepted"] == 2
    assert stats["rejected"] == 1


def test_missing_opportunity_id_is_rejected(manager):
    with pytest.raises(ValueError, match="opportunity_id is required"):
        manager.evaluate("")


def test_negative_cooldown_is_rejected(clock):
    with pytest.raises(ValueError, match="cooldown_seconds cannot be negative"):
        OpportunityDeduplicationCooldownManager(
            cooldown_seconds=-1,
            clock=clock.now,
        )
