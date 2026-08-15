from core.lbank_venue_capability_profile import (
    build_lbank_venue_capability_profile,
)


def test_lbank_profile_reflects_full_verified_capabilities():
    profile = (
        build_lbank_venue_capability_profile()
    )

    assert profile == {
        "market_data": True,
        "order_books": True,
        "networks": True,
        "transfer_metadata": True,
        "verification": True,
    }


def test_lbank_profile_is_not_partial():
    profile = (
        build_lbank_venue_capability_profile()
    )

    assert profile[
        "market_data"
    ] is True

    assert profile[
        "order_books"
    ] is True

    assert profile[
        "networks"
    ] is True

    assert profile[
        "transfer_metadata"
    ] is True

    assert profile[
        "verification"
    ] is True
