import pytest

from core.continuous_live_paper_trading_service import (
    ContinuousLivePaperTradingService,
)


class FakeScheduler:
    def __init__(self):
        self.results = [
            {"opportunity_id": "OPP-001", "status": "COMPLETED"},
            {"opportunity_id": "OPP-002", "status": "REJECTED"},
        ]

    def process_next(self):
        if not self.results:
            return None
        return self.results.pop(0)


    def pending_count(self):
        return len(self.results)


@pytest.fixture
def service():
    return ContinuousLivePaperTradingService(FakeScheduler())


def test_run_processes_all_pending_opportunities(service):
    result = service.run()

    assert result["processed"] == 2
    assert result["completed"] == 1
    assert result["rejected"] == 1
    assert result["running"] is False


def test_run_records_each_result(service):
    service.run()

    history = service.history()
    assert len(history) == 2
    assert history[0]["opportunity_id"] == "OPP-001"
    assert history[1]["opportunity_id"] == "OPP-002"


def test_stop_marks_service_not_running(service):
    service.start()
    assert service.is_running() is True

    result = service.stop()

    assert result["stopped"] is True
    assert service.is_running() is False


def test_missing_scheduler_is_rejected():
    with pytest.raises(ValueError, match="scheduler is required"):
        ContinuousLivePaperTradingService(None)
