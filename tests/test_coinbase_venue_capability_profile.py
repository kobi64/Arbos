from core.coinbase_venue_capability_profile import (
    build_coinbase_venue_capability_profile,
)


def test_coinbase_market_data_is_available():
    profile = (
        build_coinbase_venue_capability_profile()
    )

    assert profile["market_data"] is True
    assert profile["order_books"] is True


def test_coinbase_network_metadata_is_available():
    profile = (
        build_coinbase_venue_capability_profile()
    )

    assert profile["networks"] is True


def test_coinbase_transfer_metadata_is_available():
    profile = (
        build_coinbase_venue_capability_profile()
    )

    assert profile[
        "transfer_metadata"
    ] is True


def test_coinbase_verification_is_available():
    profile = (
        build_coinbase_venue_capability_profile()
    )

    assert profile["verification"] is True


def test_coinbase_profile_matches_verified_capabilities():
    profile = (
        build_coinbase_venue_capability_profile()
    )

    assert profile == {
        "market_data": True,
        "order_books": True,
        "networks": True,
        "transfer_metadata": True,
        "verification": True,
    }
