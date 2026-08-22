from core.ex373_persistent_feed_soak_benchmark import (
    BENCHMARK_HEARTBEAT_TIMEOUT_SECONDS,
    BENCHMARK_MAX_LATENCY_MS,
    EXCHANGE_IDS,
    HEALTH_SNAPSHOT_INTERVAL_SECONDS,
    SOAK_DURATION_SECONDS,
)


def test_soak_uses_nine_exchange_topology():
    assert len(EXCHANGE_IDS) == 9
    assert len(set(EXCHANGE_IDS)) == 9


def test_soak_duration_is_two_minutes():
    assert SOAK_DURATION_SECONDS == 120.0


def test_health_snapshots_are_every_30_seconds():
    assert (
        HEALTH_SNAPSHOT_INTERVAL_SECONDS
        == 30.0
    )


def test_all_exchanges_have_benchmark_health_thresholds():
    assert set(
        BENCHMARK_HEARTBEAT_TIMEOUT_SECONDS
    ) == set(EXCHANGE_IDS)


def test_xt_preserves_longer_heartbeat_window():
    assert (
        BENCHMARK_HEARTBEAT_TIMEOUT_SECONDS[
            "xt"
        ]
        == 60.0
    )


def test_other_venues_use_conservative_30_second_window():
    for exchange_id in EXCHANGE_IDS:
        if exchange_id == "xt":
            continue

        assert (
            BENCHMARK_HEARTBEAT_TIMEOUT_SECONDS[
                exchange_id
            ]
            == 30.0
        )


def test_benchmark_latency_threshold_is_conservative():
    assert BENCHMARK_MAX_LATENCY_MS == 1000.0


def test_benchmark_health_monitor_accepts_configured_thresholds():
    from core.scanner_health_monitor import (
        ScannerHealthMonitor,
    )

    for exchange_id in EXCHANGE_IDS:
        monitor = ScannerHealthMonitor(
            heartbeat_timeout_seconds=(
                BENCHMARK_HEARTBEAT_TIMEOUT_SECONDS[
                    exchange_id
                ]
            ),
            max_latency_ms=(
                BENCHMARK_MAX_LATENCY_MS
            ),
        )

        assert monitor is not None






def test_persistent_route_pool_is_available():
    from core.persistent_route_worker_pool import (
        PersistentRouteWorkerPool,
    )

    assert PersistentRouteWorkerPool is not None


def test_soak_preserves_ex372_subscription_pacing_profile():
    from core.ex373_persistent_feed_soak_benchmark import (
        SUBSCRIPTION_START_STAGGER_SECONDS,
    )

    assert SUBSCRIPTION_START_STAGGER_SECONDS == {
        "binance": 0.5,
        "bitget": 0.10,
        "gate": 0.10,
        "kucoin": 0.25,
        "poloniex": 0.10,
        "xt": 1.00,
    }


def test_soak_final_shutdown_drains_spawn_tasks_before_close():
    from pathlib import Path

    source = Path(
        "core/ex373_persistent_feed_soak_benchmark.py"
    ).read_text()

    finally_block = source[source.index("    finally:"):]

    drain_index = finally_block.index(
        "exchange.drain_spawn_tasks("
    )
    close_index = finally_block.index(
        "exchange.close()"
    )

    assert drain_index < close_index
