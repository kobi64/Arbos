from core.coinex_venue_capability_profile import (
    build_coinex_venue_capability_profile,
)


def test_coinex_market_data_is_available():
    profile = (
        build_coinex_venue_capability_profile()
    )

    assert profile["market_data"] is True
    assert profile["order_books"] is True


def test_coinex_network_metadata_is_available():
    profile = (
        build_coinex_venue_capability_profile()
    )

    assert profile["networks"] is True
    assert profile["transfer_metadata"] is True


def test_coinex_verification_is_available():
    profile = (
        build_coinex_venue_capability_profile()
    )

    assert profile["verification"] is True


def test_coinex_profile_is_full():
    profile = (
        build_coinex_venue_capability_profile()
    )

    assert all(
        profile.values()
    )
