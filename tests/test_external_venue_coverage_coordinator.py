from core.external_venue_coverage_coordinator import (
    ExternalVenueCoverageCoordinator,
)
from core.external_venue_capability_registry import (
    ExternalVenueCapabilityRegistry,
)
from core.external_venue_coverage_demand_tracker import (
    ExternalVenueCoverageDemandTracker,
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


def build_coordinator():
    registry = ExternalVenueCapabilityRegistry(
        capabilities={
            "kucoin": capability(),
            "bitget": capability(),
            "binance": capability(
                networks=False,
                transfer_metadata=False,
                verification=False,
            ),
        }
    )

    tracker = (
        ExternalVenueCoverageDemandTracker()
    )

    return ExternalVenueCoverageCoordinator(
        registry=registry,
        tracker=tracker,
    )


def opportunity(
    key,
    buy_exchange,
    sell_exchange,
    sources=None,
):
    return {
        "opportunity_key": key,
        "buy_exchange": buy_exchange,
        "sell_exchange": sell_exchange,
        "sources": sources or ["finder"],
    }


def test_full_route_is_marked_fully_verifiable():
    coordinator = build_coordinator()

    result = coordinator.evaluate(
        [
            opportunity(
                "ARB:kucoin:bitget",
                "kucoin",
                "bitget",
            )
        ]
    )

    route = result["routes"][0]

    assert route["coverage"] == "full"
    assert (
        route[
            "full_verification_available"
        ]
        is True
    )


def test_unsupported_route_is_not_fully_verifiable():
    coordinator = build_coordinator()

    result = coordinator.evaluate(
        [
            opportunity(
                "VANRY:bingx:kucoin",
                "bingx",
                "kucoin",
            )
        ]
    )

    route = result["routes"][0]

    assert route["coverage"] == "unsupported"
    assert (
        route[
            "full_verification_available"
        ]
        is False
    )

    assert "bingx" in route[
        "unsupported_exchanges"
    ]


def test_partial_route_is_preserved():
    coordinator = build_coordinator()

    result = coordinator.evaluate(
        [
            opportunity(
                "FLOW:binance:kucoin",
                "binance",
                "kucoin",
            )
        ]
    )

    route = result["routes"][0]

    assert route["coverage"] == "partial"


def test_demand_ranking_is_generated():
    coordinator = build_coordinator()

    opportunities = []

    for index in range(4):
        opportunities.append(
            opportunity(
                f"VANRY{index}:bingx:kucoin",
                "bingx",
                "kucoin",
            )
        )

    opportunities.append(
        opportunity(
            "FLOW:kraken:kucoin",
            "kraken",
            "kucoin",
        )
    )

    result = coordinator.evaluate(
        opportunities
    )

    ranking = result[
        "integration_priority"
    ]

    assert ranking[0][
        "exchange"
    ] == "bingx"

    assert ranking[0][
        "unsupported_mentions"
    ] == 4


def test_summary_counts_coverage_levels():
    coordinator = build_coordinator()

    result = coordinator.evaluate(
        [
            opportunity(
                "A:kucoin:bitget",
                "kucoin",
                "bitget",
            ),
            opportunity(
                "B:binance:kucoin",
                "binance",
                "kucoin",
            ),
            opportunity(
                "C:bingx:kucoin",
                "bingx",
                "kucoin",
            ),
        ]
    )

    assert result["route_count"] == 3
    assert result["full_count"] == 1
    assert result["partial_count"] == 1
    assert result["unsupported_count"] == 1


def test_original_opportunity_information_is_preserved():
    coordinator = build_coordinator()

    result = coordinator.evaluate(
        [
            opportunity(
                "VANRY:bingx:kucoin",
                "bingx",
                "kucoin",
                sources=[
                    "finder",
                    "coinmarketgap",
                ],
            )
        ]
    )

    route = result["routes"][0]

    assert route[
        "opportunity_key"
    ] == "VANRY:bingx:kucoin"

    assert route[
        "sources"
    ] == [
        "finder",
        "coinmarketgap",
    ]


def test_coordinator_is_paper_safe():
    coordinator = build_coordinator()

    result = coordinator.evaluate([])

    assert result["paper_only"] is True
    assert (
        result["live_order_submitted"]
        is False
    )
