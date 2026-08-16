from core.phemex_venue_capability_profile import (
    build_phemex_venue_capability_profile,
)


def test_phemex_market_data_is_available():
    profile = (
        build_phemex_venue_capability_profile()
    )

    assert profile["market_data"] is True
    assert profile["order_books"] is True


def test_phemex_network_discovery_is_available():
    profile = (
        build_phemex_venue_capability_profile()
    )

    assert profile["networks"] is True


def test_phemex_transfer_metadata_is_not_verified():
    profile = (
        build_phemex_venue_capability_profile()
    )

    assert profile[
        "transfer_metadata"
    ] is False


def test_phemex_verification_is_available():
    profile = (
        build_phemex_venue_capability_profile()
    )

    assert profile["verification"] is True


def test_phemex_profile_is_not_full_transfer_capability():
    profile = (
        build_phemex_venue_capability_profile()
    )

    assert profile == {
        "market_data": True,
        "order_books": True,
        "networks": True,
        "transfer_metadata": False,
        "verification": True,
    }
