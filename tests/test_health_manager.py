from exchanges.health_manager import (
    ExchangeHealth,
    HealthManager,
)


def test_new_health_record_preserves_unmeasured_metrics_as_unknown():
    health = ExchangeHealth(
        exchange="test",
    )

    assert health.rest_latency_ms is None
    assert health.websocket_latency_ms is None
    assert health.error_rate is None
    assert health.health_score is None
    assert health.last_check is None


def test_status_is_unknown_before_health_score_is_calculated():
    manager = HealthManager()

    health = ExchangeHealth(
        exchange="test",
    )

    assert manager.status(health) == "UNKNOWN"


def test_genuine_zero_metrics_remain_numeric_zero():
    health = ExchangeHealth(
        exchange="test",
        online=True,
        authenticated=True,
        rest_latency_ms=0.0,
        websocket_latency_ms=0.0,
        error_rate=0.0,
    )

    assert health.rest_latency_ms == 0.0
    assert health.websocket_latency_ms == 0.0
    assert health.error_rate == 0.0


def test_fully_measured_healthy_exchange_scores_100():
    manager = HealthManager()

    health = ExchangeHealth(
        exchange="test",
        online=True,
        authenticated=True,
        rest_latency_ms=100.0,
        websocket_latency_ms=100.0,
        error_rate=0.0,
        maintenance=False,
    )

    score = manager.calculate_score(
        health
    )

    assert score == 100.0
    assert health.health_score == 100.0
    assert health.last_check is not None
    assert manager.status(health) == "HEALTHY"


def test_high_rest_latency_reduces_score():
    manager = HealthManager()

    health = ExchangeHealth(
        exchange="test",
        online=True,
        authenticated=True,
        rest_latency_ms=600.0,
        websocket_latency_ms=100.0,
        error_rate=0.0,
    )

    score = manager.calculate_score(
        health
    )

    assert score == 90.0


def test_high_websocket_latency_reduces_score():
    manager = HealthManager()

    health = ExchangeHealth(
        exchange="test",
        online=True,
        authenticated=True,
        rest_latency_ms=100.0,
        websocket_latency_ms=600.0,
        error_rate=0.0,
    )

    score = manager.calculate_score(
        health
    )

    assert score == 90.0


def test_error_rate_reduces_score():
    manager = HealthManager()

    health = ExchangeHealth(
        exchange="test",
        online=True,
        authenticated=True,
        rest_latency_ms=100.0,
        websocket_latency_ms=100.0,
        error_rate=0.10,
    )

    score = manager.calculate_score(
        health
    )

    assert score == 90.0


def test_missing_rest_latency_does_not_masquerade_as_zero_latency():
    manager = HealthManager()

    health = ExchangeHealth(
        exchange="test",
        online=True,
        authenticated=True,
        rest_latency_ms=None,
        websocket_latency_ms=100.0,
        error_rate=0.0,
    )

    score = manager.calculate_score(
        health
    )

    assert score < 100.0


def test_missing_websocket_latency_does_not_masquerade_as_zero_latency():
    manager = HealthManager()

    health = ExchangeHealth(
        exchange="test",
        online=True,
        authenticated=True,
        rest_latency_ms=100.0,
        websocket_latency_ms=None,
        error_rate=0.0,
    )

    score = manager.calculate_score(
        health
    )

    assert score < 100.0


def test_missing_error_rate_does_not_masquerade_as_zero_error_rate():
    manager = HealthManager()

    health = ExchangeHealth(
        exchange="test",
        online=True,
        authenticated=True,
        rest_latency_ms=100.0,
        websocket_latency_ms=100.0,
        error_rate=None,
    )

    score = manager.calculate_score(
        health
    )

    assert score < 100.0


def test_all_missing_telemetry_cannot_score_as_healthy():
    manager = HealthManager()

    health = ExchangeHealth(
        exchange="test",
        online=True,
        authenticated=True,
    )

    score = manager.calculate_score(
        health
    )

    assert score < 90.0
    assert manager.status(health) != "HEALTHY"


def test_offline_exchange_remains_heavily_penalized():
    manager = HealthManager()

    health = ExchangeHealth(
        exchange="test",
        online=False,
        authenticated=True,
        rest_latency_ms=100.0,
        websocket_latency_ms=100.0,
        error_rate=0.0,
    )

    score = manager.calculate_score(
        health
    )

    assert score == 50.0
    assert manager.status(health) == "DEGRADED"


def test_maintenance_exchange_cannot_score_healthy():
    manager = HealthManager()

    health = ExchangeHealth(
        exchange="test",
        online=True,
        authenticated=True,
        rest_latency_ms=100.0,
        websocket_latency_ms=100.0,
        error_rate=0.0,
        maintenance=True,
    )

    score = manager.calculate_score(
        health
    )

    assert score == 50.0
    assert manager.status(health) == "DEGRADED"
