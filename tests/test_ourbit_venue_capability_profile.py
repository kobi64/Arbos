from core.ourbit_venue_capability_profile import (
    build_ourbit_venue_capability_profile,
)


def test_ourbit_profile_reflects_current_capabilities():
    profile = (
        build_ourbit_venue_capability_profile()
    )

    assert profile == {
        "market_data": True,
        "order_books": True,
        "networks": False,
        "transfer_metadata": False,
        "verification": False,
    }


def test_ourbit_profile_does_not_overstate_transfer_support():
    profile = (
        build_ourbit_venue_capability_profile()
    )

    assert profile[
        "market_data"
    ] is True

    assert profile[
        "order_books"
    ] is True

    assert profile[
        "networks"
    ] is False

    assert profile[
        "transfer_metadata"
    ] is False

    assert profile[
        "verification"
    ] is False
