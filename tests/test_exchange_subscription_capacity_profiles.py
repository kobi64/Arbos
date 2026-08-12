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


def test_profile_preserves_verified_capacity_metadata():
    profiles = ExchangeSubscriptionCapacityProfiles()

    profile = kucoin_profile()

    profile[
        "verified_capacity"
    ] = {
        "max_topics_per_connection": 400,
        "max_topics_per_request": 100,
        "client_messages_per_window": 100,
        "client_message_window_seconds": 10,
    }

    profiles.register(profile)

    result = profiles.get(
        "kucoin"
    )

    assert result[
        "verified_capacity"
    ][
        "max_topics_per_connection"
    ] == 400

    assert result[
        "verified_capacity"
    ][
        "max_topics_per_request"
    ] == 100


def test_profile_preserves_provenance_metadata():
    profiles = ExchangeSubscriptionCapacityProfiles()

    profile = kucoin_profile()

    profile[
        "provenance"
    ] = {
        "source_type": "official_exchange_documentation",
        "verified": True,
        "verified_date": "2026-08-12",
    }

    profiles.register(profile)

    result = profiles.get(
        "kucoin"
    )

    assert result[
        "provenance"
    ][
        "source_type"
    ] == "official_exchange_documentation"

    assert result[
        "provenance"
    ][
        "verified"
    ] is True


def test_verified_metadata_remains_copy_safe():
    profiles = ExchangeSubscriptionCapacityProfiles()

    profile = kucoin_profile()

    profile[
        "verified_capacity"
    ] = {
        "max_topics_per_connection": 400,
    }

    profiles.register(profile)

    first = profiles.get(
        "kucoin"
    )

    first[
        "verified_capacity"
    ][
        "max_topics_per_connection"
    ] = 999

    second = profiles.get(
        "kucoin"
    )

    assert second[
        "verified_capacity"
    ][
        "max_topics_per_connection"
    ] == 400
