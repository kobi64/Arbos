import pytest

from core.exchange_feed_configuration_factory import (
    ExchangeFeedConfigurationFactory,
)

from core.live_feed_subscription_batch_planner import (
    LiveFeedSubscriptionBatchPlanner,
)

from core.live_feed_health_supervisor import (
    LiveFeedHealthSupervisor,
)

from exchanges.order_retry_backoff_policy import (
    OrderRetryBackoffPolicy,
)


class FakeProfiles:
    def __init__(self, profile=None):
        self.profile = profile
        self.calls = []

    def get(self, exchange_id):
        self.calls.append(exchange_id)
        return self.profile


def profile():
    return {
        "exchange_id": "kucoin",
        "max_symbols_per_batch": 100,
        "max_batches": 5,
        "max_total_symbols": 500,
        "retry_base_delay_seconds": 2.0,
        "retry_max_delay_seconds": 20.0,
        "heartbeat_timeout_seconds": 30.0,
        "max_latency_ms": 750.0,
    }


def test_builds_exchange_feed_configuration():
    profiles = FakeProfiles(
        profile()
    )

    factory = ExchangeFeedConfigurationFactory(
        profiles=profiles
    )

    result = factory.build(
        " KUCOIN "
    )

    assert profiles.calls == [
        "kucoin",
    ]

    assert result[
        "exchange_id"
    ] == "kucoin"

    assert isinstance(
        result["batch_planner"],
        LiveFeedSubscriptionBatchPlanner,
    )

    assert isinstance(
        result["health_supervisor"],
        LiveFeedHealthSupervisor,
    )

    assert isinstance(
        result["backoff_policy"],
        OrderRetryBackoffPolicy,
    )

    assert result[
        "paper_only"
    ] is True

    assert result[
        "live_order_submitted"
    ] is False


def test_batch_planner_uses_profile_capacity():
    factory = ExchangeFeedConfigurationFactory(
        profiles=FakeProfiles(
            profile()
        )
    )

    result = factory.build(
        "kucoin"
    )

    plan = result[
        "batch_planner"
    ].plan(
        exchange_id="kucoin",
        symbols=[
            f"COIN{i}/USDT"
            for i in range(501)
        ],
    )

    assert plan[
        "max_symbols_per_batch"
    ] == 100

    assert plan[
        "max_batches"
    ] == 5

    assert plan[
        "capacity"
    ] == 500

    assert plan[
        "selected_symbol_count"
    ] == 500

    assert len(
        plan["overflow_symbols"]
    ) == 1


def test_backoff_policy_uses_profile_values():
    factory = ExchangeFeedConfigurationFactory(
        profiles=FakeProfiles(
            profile()
        )
    )

    result = factory.build(
        "kucoin"
    )

    policy = result[
        "backoff_policy"
    ]

    assert (
        policy.base_delay_seconds
        == 2.0
    )

    assert (
        policy.max_delay_seconds
        == 20.0
    )


def test_health_supervisor_uses_profile_thresholds():
    factory = ExchangeFeedConfigurationFactory(
        profiles=FakeProfiles(
            profile()
        )
    )

    result = factory.build(
        "kucoin"
    )

    health = result[
        "health_supervisor"
    ]

    healthy = health.record_success(
        exchange_id="kucoin",
        symbol="BTC/USDT",
        latency_ms=500,
    )

    degraded = health.record_success(
        exchange_id="kucoin",
        symbol="ETH/USDT",
        latency_ms=800,
    )

    assert healthy[
        "healthy"
    ] is True

    assert degraded[
        "healthy"
    ] is False

    assert degraded[
        "reason"
    ] == "latency_exceeded"


def test_unknown_exchange_is_rejected():
    factory = ExchangeFeedConfigurationFactory(
        profiles=FakeProfiles(
            None
        )
    )

    with pytest.raises(
        ValueError,
        match="exchange profile not found",
    ):
        factory.build(
            "unknown"
        )


def test_exchange_id_is_required():
    factory = ExchangeFeedConfigurationFactory(
        profiles=FakeProfiles(
            profile()
        )
    )

    with pytest.raises(
        ValueError,
        match="exchange_id is required",
    ):
        factory.build(
            ""
        )


def test_profiles_registry_is_required():
    with pytest.raises(
        ValueError,
        match="profiles is required",
    ):
        ExchangeFeedConfigurationFactory(
            profiles=None
        )
