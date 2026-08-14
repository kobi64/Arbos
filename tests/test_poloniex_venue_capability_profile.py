from core.poloniex_venue_capability_profile import (
    build_poloniex_venue_capability_profile,
)


def test_poloniex_profile_is_full_capability():
    profile = (
        build_poloniex_venue_capability_profile()
    )

    assert profile == {
        "market_data": True,
        "order_books": True,
        "networks": True,
        "transfer_metadata": True,
        "verification": True,
    }


def test_poloniex_profile_is_paper_safe():
    profile = (
        build_poloniex_venue_capability_profile()
    )

    assert profile[
        "market_data"
    ] is True

    assert profile[
        "verification"
    ] is True
