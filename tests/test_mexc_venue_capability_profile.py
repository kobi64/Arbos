from core.mexc_venue_capability_profile import (
    build_mexc_venue_capability_profile,
)


def test_mexc_profile_reflects_current_capabilities():
    profile = (
        build_mexc_venue_capability_profile()
    )

    assert profile == {
        "market_data": True,
        "order_books": True,
        "networks": True,
        "transfer_metadata": True,
        "verification": True,
    }


def test_mexc_profile_is_paper_safe():
    profile = (
        build_mexc_venue_capability_profile()
    )

    assert profile[
        "market_data"
    ] is True

    assert profile[
        "verification"
    ] is True
