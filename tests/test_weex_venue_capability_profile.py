from core.external_venue_alias_registry import (
    ExternalVenueAliasRegistry,
)
from core.external_venue_capability_registry import (
    ExternalVenueCapabilityRegistry,
)
from core.weex_venue_capability_profile import (
    build_weex_venue_capability_profile,
)


def test_weex_profile_is_full_capability():
    profile = (
        build_weex_venue_capability_profile()
    )

    assert profile == {
        "market_data": True,
        "order_books": True,
        "networks": True,
        "transfer_metadata": True,
        "verification": True,
    }


def test_weex_route_can_be_classified_full():
    capabilities = {
        "weex": (
            build_weex_venue_capability_profile()
        ),
        "kucoin": {
            "market_data": True,
            "order_books": True,
            "networks": True,
            "transfer_metadata": True,
            "verification": True,
        },
    }

    registry = ExternalVenueCapabilityRegistry(
        capabilities=capabilities,
        alias_registry=(
            ExternalVenueAliasRegistry()
        ),
    )

    result = registry.classify_route(
        buy_exchange="WEEX",
        sell_exchange="KuCoin",
    )

    assert result[
        "coverage"
    ] == "full"

    assert result[
        "full_verification_available"
    ] is True


def test_weex_is_no_longer_unsupported():
    registry = ExternalVenueCapabilityRegistry(
        capabilities={
            "weex": (
                build_weex_venue_capability_profile()
            ),
        },
        alias_registry=(
            ExternalVenueAliasRegistry()
        ),
    )

    result = registry.classify_exchange(
        "weex"
    )

    assert result[
        "coverage"
    ] == "full"

    assert result[
        "known_exchange"
    ] is True
