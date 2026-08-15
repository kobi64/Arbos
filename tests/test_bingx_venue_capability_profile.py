from core.bingx_venue_capability_profile import (
    build_bingx_venue_capability_profile,
)


def test_bingx_market_data_is_available():
    profile = (
        build_bingx_venue_capability_profile()
    )

    assert profile["market_data"] is True
    assert profile["order_books"] is True


def test_bingx_network_metadata_fails_closed():
    profile = (
        build_bingx_venue_capability_profile()
    )

    assert profile["networks"] is False
    assert profile["transfer_metadata"] is False
    assert profile["verification"] is False


def test_bingx_profile_is_not_full_capability():
    profile = (
        build_bingx_venue_capability_profile()
    )

    assert not all(
        profile.values()
    )
