from core.hotcoin_venue_capability_profile import (
    build_hotcoin_venue_capability_profile,
)


def test_hotcoin_market_data_is_available():
    profile = (
        build_hotcoin_venue_capability_profile()
    )

    assert profile["market_data"] is True


def test_hotcoin_order_books_fail_closed():
    profile = (
        build_hotcoin_venue_capability_profile()
    )

    assert profile["order_books"] is False


def test_hotcoin_transfer_metadata_fails_closed():
    profile = (
        build_hotcoin_venue_capability_profile()
    )

    assert profile["networks"] is False
    assert profile["transfer_metadata"] is False
    assert profile["verification"] is False


def test_hotcoin_profile_is_partial_not_full():
    profile = (
        build_hotcoin_venue_capability_profile()
    )

    assert not all(
        profile.values()
    )
