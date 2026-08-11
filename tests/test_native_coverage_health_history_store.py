import json

import pytest

from core.native_coverage_health_history_store import (
    NativeCoverageHealthHistoryStore,
)


class FakeClock:
    def __init__(self):
        self.value = 1000.0

    def now(self):
        return self.value

    def advance(self, seconds):
        self.value += seconds


def healthy_report():
    return {
        "status": "HEALTHY",
        "healthy": True,
        "configured_exchange_count": 6,
        "successful_exchange_count": 6,
        "failed_exchange_count": 0,
        "verified_raw_only_count": 513,
        "depth_sampled_count": 20,
        "usable_depth_count": 20,
        "fallback_available_exchange_ids": [
            "digifinex",
        ],
        "failed_exchange_ids": [],
        "report_complete": True,
        "live_order_submitted": False,
    }


def test_appends_health_report_to_jsonl(tmp_path):
    path = tmp_path / "coverage-health.jsonl"

    store = NativeCoverageHealthHistoryStore(
        path=path,
        clock=lambda: 1000.0,
    )

    result = store.append(
        healthy_report()
    )

    assert result["stored"] is True
    assert result["timestamp"] == 1000.0
    assert result["status"] == "HEALTHY"

    lines = path.read_text().splitlines()

    assert len(lines) == 1

    saved = json.loads(lines[0])

    assert saved["timestamp"] == 1000.0
    assert saved["report"]["status"] == "HEALTHY"


def test_preserves_multiple_reports_in_order(tmp_path):
    clock = FakeClock()

    path = tmp_path / "coverage-health.jsonl"

    store = NativeCoverageHealthHistoryStore(
        path=path,
        clock=clock.now,
    )

    store.append(
        healthy_report()
    )

    clock.advance(60)

    degraded = {
        **healthy_report(),
        "status": "DEGRADED",
        "healthy": False,
        "failed_exchange_count": 1,
        "failed_exchange_ids": [
            "xt",
        ],
    }

    store.append(degraded)

    history = store.history()

    assert len(history) == 2

    assert history[0]["timestamp"] == 1000.0
    assert history[0]["report"]["status"] == (
        "HEALTHY"
    )

    assert history[1]["timestamp"] == 1060.0
    assert history[1]["report"]["status"] == (
        "DEGRADED"
    )


def test_latest_returns_most_recent_report(tmp_path):
    clock = FakeClock()

    store = NativeCoverageHealthHistoryStore(
        path=tmp_path / "coverage-health.jsonl",
        clock=clock.now,
    )

    store.append(
        healthy_report()
    )

    clock.advance(10)

    degraded = {
        **healthy_report(),
        "status": "DEGRADED",
        "healthy": False,
    }

    store.append(degraded)

    latest = store.latest()

    assert latest["timestamp"] == 1010.0
    assert latest["report"]["status"] == (
        "DEGRADED"
    )


def test_latest_returns_none_when_history_empty(tmp_path):
    store = NativeCoverageHealthHistoryStore(
        path=tmp_path / "coverage-health.jsonl",
    )

    assert store.latest() is None


def test_history_limit_returns_most_recent_records(tmp_path):
    clock = FakeClock()

    store = NativeCoverageHealthHistoryStore(
        path=tmp_path / "coverage-health.jsonl",
        clock=clock.now,
    )

    for index in range(3):
        report = {
            **healthy_report(),
            "sequence": index,
        }

        store.append(report)
        clock.advance(1)

    history = store.history(
        limit=2
    )

    assert len(history) == 2
    assert history[0]["report"]["sequence"] == 1
    assert history[1]["report"]["sequence"] == 2


def test_rejects_missing_report(tmp_path):
    store = NativeCoverageHealthHistoryStore(
        path=tmp_path / "coverage-health.jsonl",
    )

    with pytest.raises(
        ValueError,
        match="health_report is required",
    ):
        store.append(None)


def test_rejects_non_positive_history_limit(tmp_path):
    store = NativeCoverageHealthHistoryStore(
        path=tmp_path / "coverage-health.jsonl",
    )

    with pytest.raises(
        ValueError,
        match="limit must be positive",
    ):
        store.history(limit=0)


def test_creates_parent_directory(tmp_path):
    path = (
        tmp_path
        / "nested"
        / "health"
        / "coverage.jsonl"
    )

    store = NativeCoverageHealthHistoryStore(
        path=path,
        clock=lambda: 1000.0,
    )

    store.append(
        healthy_report()
    )

    assert path.exists()


def test_store_is_observability_only(tmp_path):
    store = NativeCoverageHealthHistoryStore(
        path=tmp_path / "coverage-health.jsonl",
    )

    result = store.append(
        healthy_report()
    )

    assert result[
        "live_order_submitted"
    ] is False
