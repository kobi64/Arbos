import pytest

from core.external_venue_capability_registry import (
    ExternalVenueCapabilityRegistry,
)


def capability(
    market_data=True,
    order_books=True,
    networks=True,
    transfer_metadata=True,
    verification=True,
):
    return {
        "market_data": market_data,
        "order_books": order_books,
        "networks": networks,
        "transfer_metadata": transfer_metadata,
        "verification": verification,
    }


def test_fully_supported_exchange_is_full():
    registry = ExternalVenueCapabilityRegistry(
        capabilities={
            "kucoin": capability(),
        }
    )

    result = registry.classify_exchange(
        "KuCoin"
    )

    assert result[
        "exchange"
    ] == "kucoin"

    assert result[
        "coverage"
    ] == "full"

    assert result[
        "full_verification_available"
    ] is True


def test_partial_exchange_is_partial():
    registry = ExternalVenueCapabilityRegistry(
        capabilities={
            "binance": capability(
                networks=False,
                transfer_metadata=False,
                verification=False,
            ),
        }
    )

    result = registry.classify_exchange(
        "Binance"
    )

    assert result[
        "coverage"
    ] == "partial"

    assert result[
        "full_verification_available"
    ] is False


def test_intelligence_only_exchange_is_classified():
    registry = ExternalVenueCapabilityRegistry(
        capabilities={
            "ourbit": capability(
                market_data=False,
                order_books=False,
                networks=False,
                transfer_metadata=False,
                verification=False,
            ),
        }
    )

    result = registry.classify_exchange(
        "Ourbit"
    )

    assert result[
        "coverage"
    ] == "intelligence_only"

    assert result[
        "full_verification_available"
    ] is False


def test_unknown_exchange_is_unsupported():
    registry = ExternalVenueCapabilityRegistry(
        capabilities={}
    )

    result = registry.classify_exchange(
        "MysteryExchange"
    )

    assert result[
        "coverage"
    ] == "unsupported"

    assert result[
        "known_exchange"
    ] is False


def test_route_requires_both_exchanges_for_full_verification():
    registry = ExternalVenueCapabilityRegistry(
        capabilities={
            "kucoin": capability(),
            "bitget": capability(),
        }
    )

    result = registry.classify_route(
        buy_exchange="KuCoin",
        sell_exchange="Bitget",
    )

    assert result[
        "coverage"
    ] == "full"

    assert result[
        "full_verification_available"
    ] is True


def test_one_unsupported_exchange_blocks_full_route_verification():
    registry = ExternalVenueCapabilityRegistry(
        capabilities={
            "kucoin": capability(),
        }
    )

    result = registry.classify_route(
        buy_exchange="KuCoin",
        sell_exchange="BingX",
    )

    assert result[
        "coverage"
    ] != "full"

    assert result[
        "full_verification_available"
    ] is False

    assert "bingx" in result[
        "unsupported_exchanges"
    ]


def test_same_exchange_route_is_rejected():
    registry = ExternalVenueCapabilityRegistry(
        capabilities={
            "kucoin": capability(),
        }
    )

    with pytest.raises(
        ValueError,
        match="buy and sell exchanges must be distinct",
    ):
        registry.classify_route(
            buy_exchange="KuCoin",
            sell_exchange="KuCoin",
        )


def test_missing_exchange_is_rejected():
    registry = ExternalVenueCapabilityRegistry(
        capabilities={}
    )

    with pytest.raises(
        ValueError,
        match="exchange is required",
    ):
        registry.classify_exchange("")


def test_route_classification_uses_exchange_aliases():
    from core.external_venue_alias_registry import (
        ExternalVenueAliasRegistry,
    )

    registry = ExternalVenueCapabilityRegistry(
        capabilities={
            "gateio": capability(),
            "htx": capability(),
        },
        alias_registry=ExternalVenueAliasRegistry(),
    )

    result = registry.classify_route(
        buy_exchange="Gate",
        sell_exchange="Huobi",
    )

    assert result[
        "buy_exchange"
    ] == "gateio"

    assert result[
        "sell_exchange"
    ] == "htx"

    assert result[
        "coverage"
    ] == "full"

    assert result[
        "full_verification_available"
    ] is True


def test_exchange_classification_uses_aliases():
    from core.external_venue_alias_registry import (
        ExternalVenueAliasRegistry,
    )

    registry = ExternalVenueCapabilityRegistry(
        capabilities={
            "gateio": capability(),
        },
        alias_registry=ExternalVenueAliasRegistry(),
    )

    result = registry.classify_exchange(
        "Gate.io"
    )

    assert result[
        "exchange"
    ] == "gateio"

    assert result[
        "coverage"
    ] == "full"


def test_alias_registry_is_optional():
    registry = ExternalVenueCapabilityRegistry(
        capabilities={
            "kucoin": capability(),
        }
    )

    result = registry.classify_exchange(
        "KuCoin"
    )

    assert result[
        "exchange"
    ] == "kucoin"

    assert result[
        "coverage"
    ] == "full"
