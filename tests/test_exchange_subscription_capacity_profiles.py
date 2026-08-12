import pytest

from core.exchange_subscription_capacity_profiles import (
    ExchangeSubscriptionCapacityProfiles,
)


def kucoin_profile():
    return {
        "exchange_id": "kucoin",
        "max_symbols_per_batch": 100,
        "max_batches": 5,
        "retry_base_delay_seconds": 1.0,
        "retry_max_delay_seconds": 30.0,
        "heartbeat_timeout_seconds": 30.0,
        "max_latency_ms": 1000.0,
    }


def test_registers_and_returns_profile():
    profiles = ExchangeSubscriptionCapacityProfiles()

    result = profiles.register(
        kucoin_profile()
    )

    assert result["registered"] is True
    assert result["exchange_id"] == "kucoin"

    profile = profiles.get(
        "kucoin"
    )

    assert profile[
        "max_symbols_per_batch"
    ] == 100

    assert profile[
        "max_batches"
    ] == 5

    assert profile[
        "max_total_symbols"
    ] == 500


def test_normalizes_exchange_id():
    profiles = ExchangeSubscriptionCapacityProfiles()

    profile = kucoin_profile()
    profile["exchange_id"] = " KUCOIN "

    profiles.register(profile)

    assert profiles.get(
        "kucoin"
    )[
        "exchange_id"
    ] == "kucoin"


def test_profiles_are_copy_safe():
    profiles = ExchangeSubscriptionCapacityProfiles()

    profiles.register(
        kucoin_profile()
    )

    first = profiles.get(
        "kucoin"
    )

    first[
        "max_symbols_per_batch"
    ] = 999

    second = profiles.get(
        "kucoin"
    )

    assert second[
        "max_symbols_per_batch"
    ] == 100


def test_duplicate_exchange_profile_is_rejected():
    profiles = ExchangeSubscriptionCapacityProfiles()

    profiles.register(
        kucoin_profile()
    )

    with pytest.raises(
        ValueError,
        match="exchange profile already registered",
    ):
        profiles.register(
            kucoin_profile()
        )


def test_unknown_exchange_returns_none():
    profiles = ExchangeSubscriptionCapacityProfiles()

    assert profiles.get(
        "unknown"
    ) is None


def test_required_fields_are_validated():
    profiles = ExchangeSubscriptionCapacityProfiles()

    profile = kucoin_profile()
    profile.pop("exchange_id")

    with pytest.raises(
        ValueError,
        match="exchange_id is required",
    ):
        profiles.register(profile)

    profile = kucoin_profile()
    profile["max_symbols_per_batch"] = 0

    with pytest.raises(
        ValueError,
        match="max_symbols_per_batch must be positive",
    ):
        profiles.register(profile)

    profile = kucoin_profile()
    profile["max_batches"] = 0

    with pytest.raises(
        ValueError,
        match="max_batches must be positive",
    ):
        profiles.register(profile)


def test_retry_and_health_values_must_be_non_negative():
    profiles = ExchangeSubscriptionCapacityProfiles()

    profile = kucoin_profile()
    profile["retry_base_delay_seconds"] = -1

    with pytest.raises(
        ValueError,
        match="retry_base_delay_seconds cannot be negative",
    ):
        profiles.register(profile)

    profile = kucoin_profile()
    profile["max_latency_ms"] = -1

    with pytest.raises(
        ValueError,
        match="max_latency_ms cannot be negative",
    ):
        profiles.register(profile)


def test_profile_count_tracks_registered_exchanges():
    profiles = ExchangeSubscriptionCapacityProfiles()

    profiles.register(
        kucoin_profile()
    )

    second = kucoin_profile()
    second["exchange_id"] = "gate"

    profiles.register(second)

    assert profiles.profile_count() == 2


def test_profile_is_paper_safe():
    profiles = ExchangeSubscriptionCapacityProfiles()

    profiles.register(
        kucoin_profile()
    )

    profile = profiles.get(
        "kucoin"
    )

    assert profile["paper_only"] is True
    assert profile[
        "live_order_submitted"
    ] is False
