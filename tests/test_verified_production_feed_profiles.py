from core.exchange_subscription_capacity_profiles import (
    ExchangeSubscriptionCapacityProfiles,
)
from core.verified_production_feed_profiles import (
    VerifiedProductionFeedProfiles,
)


def test_registers_initial_verified_profiles():
    registry = ExchangeSubscriptionCapacityProfiles()

    result = VerifiedProductionFeedProfiles().register_all(
        registry
    )

    assert result["registered_count"] == 6

    assert registry.profile_count() == 6

    assert set(
        result["exchange_ids"]
    ) == {
        "kucoin",
        "bitget",
        "gate",
        "digifinex",
        "htx",
        "xt",
    }


def test_kucoin_profile_separates_verified_limits_from_policy():
    registry = ExchangeSubscriptionCapacityProfiles()

    VerifiedProductionFeedProfiles().register_all(
        registry
    )

    profile = registry.get(
        "kucoin"
    )

    assert profile[
        "max_symbols_per_batch"
    ] == 80

    assert profile[
        "max_batches"
    ] == 4

    assert profile[
        "max_total_symbols"
    ] == 320

    verified = profile[
        "verified_capacity"
    ]

    assert verified[
        "max_topics_per_connection"
    ] == 400

    assert verified[
        "max_topics_per_request"
    ] == 100

    assert verified[
        "client_messages_per_window"
    ] == 100

    assert verified[
        "client_message_window_seconds"
    ] == 10


def test_bitget_profile_uses_conservative_channel_policy():
    registry = ExchangeSubscriptionCapacityProfiles()

    VerifiedProductionFeedProfiles().register_all(
        registry
    )

    profile = registry.get(
        "bitget"
    )

    assert profile[
        "max_symbols_per_batch"
    ] == 40

    assert profile[
        "max_batches"
    ] == 5

    assert profile[
        "max_total_symbols"
    ] == 200

    verified = profile[
        "verified_capacity"
    ]

    assert verified[
        "max_channels_per_connection"
    ] == 1000

    assert verified[
        "recommended_channels_per_connection_less_than"
    ] == 50

    assert verified[
        "max_connections_per_ip"
    ] == 100

    assert verified[
        "client_messages_per_second"
    ] == 10


def test_profiles_include_verification_provenance():
    registry = ExchangeSubscriptionCapacityProfiles()

    VerifiedProductionFeedProfiles().register_all(
        registry
    )

    for exchange_id in [
        "kucoin",
        "bitget",
    ]:
        profile = registry.get(
            exchange_id
        )

        provenance = profile[
            "provenance"
        ]

        assert provenance[
            "source_type"
        ] == "official_exchange_documentation"

        assert provenance[
            "verified"
        ] is True

        assert provenance[
            "verified_date"
        ] == "2026-08-12"


def test_profiles_mark_operating_values_as_arbos_policy():
    registry = ExchangeSubscriptionCapacityProfiles()

    VerifiedProductionFeedProfiles().register_all(
        registry
    )

    for exchange_id in [
        "kucoin",
        "bitget",
    ]:
        profile = registry.get(
            exchange_id
        )

        assert profile[
            "operating_policy"
        ][
            "policy_owner"
        ] == "ArbOS"

        assert profile[
            "operating_policy"
        ][
            "conservative_capacity"
        ] is True


def test_profiles_remain_paper_safe():
    registry = ExchangeSubscriptionCapacityProfiles()

    VerifiedProductionFeedProfiles().register_all(
        registry
    )

    for exchange_id in [
        "kucoin",
        "bitget",
    ]:
        profile = registry.get(
            exchange_id
        )

        assert profile["paper_only"] is True
        assert (
            profile["live_order_submitted"]
            is False
        )


def test_registers_gate_and_digifinex_profiles():
    registry = ExchangeSubscriptionCapacityProfiles()

    result = VerifiedProductionFeedProfiles().register_all(
        registry
    )

    assert result["registered_count"] == 6

    assert {
        "gate",
        "digifinex",
    }.issubset(
        set(
            result["exchange_ids"]
        )
    )


def test_gate_profile_separates_documented_and_policy_limits():
    registry = ExchangeSubscriptionCapacityProfiles()

    VerifiedProductionFeedProfiles().register_all(
        registry
    )

    profile = registry.get(
        "gate"
    )

    assert profile[
        "max_symbols_per_batch"
    ] == 50

    assert profile[
        "max_batches"
    ] == 4

    assert profile[
        "max_total_symbols"
    ] == 200

    verified = profile[
        "verified_capacity"
    ]

    assert verified[
        "max_connections_per_ip"
    ] == 300

    assert verified[
        "documented_symbol_limit"
    ] is None


def test_digifinex_profile_marks_multi_symbol_support():
    registry = ExchangeSubscriptionCapacityProfiles()

    VerifiedProductionFeedProfiles().register_all(
        registry
    )

    profile = registry.get(
        "digifinex"
    )

    assert profile[
        "max_symbols_per_batch"
    ] == 40

    assert profile[
        "max_batches"
    ] == 4

    assert profile[
        "max_total_symbols"
    ] == 160

    verified = profile[
        "verified_capacity"
    ]

    assert verified[
        "multi_symbol_subscription_supported"
    ] is True

    assert verified[
        "documented_symbol_limit"
    ] is None


def test_unpublished_capacity_is_explicit_not_guessed():
    registry = ExchangeSubscriptionCapacityProfiles()

    VerifiedProductionFeedProfiles().register_all(
        registry
    )

    for exchange_id in [
        "gate",
        "digifinex",
    ]:
        profile = registry.get(
            exchange_id
        )

        assert profile[
            "verified_capacity"
        ][
            "documented_symbol_limit"
        ] is None

        assert profile[
            "operating_policy"
        ][
            "capacity_source"
        ] == "ArbOS_conservative_policy"


def test_registers_all_six_initial_production_exchanges():
    registry = ExchangeSubscriptionCapacityProfiles()

    result = VerifiedProductionFeedProfiles().register_all(
        registry
    )

    assert result["registered_count"] == 6

    assert set(result["exchange_ids"]) == {
        "kucoin",
        "bitget",
        "gate",
        "digifinex",
        "htx",
        "xt",
    }

    assert registry.profile_count() == 6


def test_htx_profile_does_not_invent_symbol_ceiling():
    registry = ExchangeSubscriptionCapacityProfiles()

    VerifiedProductionFeedProfiles().register_all(
        registry
    )

    profile = registry.get("htx")

    assert profile["max_symbols_per_batch"] == 40
    assert profile["max_batches"] == 4
    assert profile["max_total_symbols"] == 160

    verified = profile["verified_capacity"]

    assert verified["documented_symbol_limit"] is None
    assert verified["server_ping_interval_seconds"] == 5

    assert (
        profile["operating_policy"]["capacity_source"]
        == "ArbOS_conservative_policy"
    )


def test_xt_profile_preserves_documented_depth_limit():
    registry = ExchangeSubscriptionCapacityProfiles()

    VerifiedProductionFeedProfiles().register_all(
        registry
    )

    profile = registry.get("xt")

    assert profile["max_symbols_per_batch"] == 10
    assert profile["max_batches"] == 8
    assert profile["max_total_symbols"] == 80

    verified = profile["verified_capacity"]

    assert verified[
        "max_pairs_per_multi_depth_subscription"
    ] == 10

    assert verified[
        "heartbeat_disconnect_seconds_approx"
    ] == 60


def test_htx_and_xt_capacity_policy_is_explicit():
    registry = ExchangeSubscriptionCapacityProfiles()

    VerifiedProductionFeedProfiles().register_all(
        registry
    )

    for exchange_id in ["htx", "xt"]:
        profile = registry.get(exchange_id)

        assert (
            profile["operating_policy"]["policy_owner"]
            == "ArbOS"
        )

        assert (
            profile["operating_policy"]["conservative_capacity"]
            is True
        )

        assert (
            profile["operating_policy"]["capacity_source"]
            == "ArbOS_conservative_policy"
        )
