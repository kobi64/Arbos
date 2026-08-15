from core.htx_venue_capability_profile import (
    build_htx_venue_capability_profile,
)


def test_htx_market_data_is_available():
    profile = (
        build_htx_venue_capability_profile()
    )

    assert profile["market_data"] is True
    assert profile["order_books"] is True


def test_htx_transfer_metadata_fails_closed():
    profile = (
        build_htx_venue_capability_profile()
    )

    assert profile["networks"] is False
    assert profile["transfer_metadata"] is False
    assert profile["verification"] is False


def test_htx_profile_is_partial_not_full():
    profile = (
        build_htx_venue_capability_profile()
    )

    assert not all(
        profile.values()
    )
