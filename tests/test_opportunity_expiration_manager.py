import pytest

from core.opportunity_expiration_manager import (
    OpportunityExpirationManager,
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
    return OpportunityExpirationManager(
        ttl_seconds=30,
        clock=clock.now,
    )


def test_fresh_opportunity_is_valid(manager):
    result = manager.evaluate(
        opportunity_id="OPP-001",
        created_at=995.0,
    )

    assert result["expired"] is False
    assert result["reason"] is None


def test_old_opportunity_expires(manager):
    result = manager.evaluate(
        opportunity_id="OPP-002",
        created_at=960.0,
    )

    assert result["expired"] is True
    assert result["reason"] == "opportunity_expired"


def test_opportunity_expires_at_ttl_boundary(manager):
    result = manager.evaluate(
        opportunity_id="OPP-003",
        created_at=970.0,
    )

    assert result["expired"] is True
    assert result["age_seconds"] == 30.0


def test_missing_opportunity_id_is_rejected(manager):
    with pytest.raises(ValueError, match="opportunity_id is required"):
        manager.evaluate(
            opportunity_id="",
            created_at=995.0,
        )


def test_negative_ttl_is_rejected(clock):
    with pytest.raises(ValueError, match="ttl_seconds cannot be negative"):
        OpportunityExpirationManager(
            ttl_seconds=-1,
            clock=clock.now,
        )
