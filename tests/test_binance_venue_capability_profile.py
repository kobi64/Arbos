from core.binance_venue_capability_profile import (
    build_binance_venue_capability_profile,
)


def test_binance_market_data_is_available():
    profile = (
        build_binance_venue_capability_profile()
    )

    assert profile["market_data"] is True
    assert profile["order_books"] is True


def test_binance_public_network_metadata_is_not_available():
    profile = (
        build_binance_venue_capability_profile()
    )

    assert profile["networks"] is False


def test_binance_transfer_metadata_is_not_available():
    profile = (
        build_binance_venue_capability_profile()
    )

    assert profile[
        "transfer_metadata"
    ] is False


def test_binance_verification_is_available():
    profile = (
        build_binance_venue_capability_profile()
    )

    assert profile["verification"] is True


def test_binance_profile_is_fail_closed_for_transfers():
    profile = (
        build_binance_venue_capability_profile()
    )

    assert profile == {
        "market_data": True,
        "order_books": True,
        "networks": False,
        "transfer_metadata": False,
        "verification": True,
    }
