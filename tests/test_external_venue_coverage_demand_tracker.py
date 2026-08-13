from core.external_venue_coverage_demand_tracker import (
    ExternalVenueCoverageDemandTracker,
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


def test_tracks_unsupported_exchange_mentions():
    tracker = ExternalVenueCoverageDemandTracker()

    tracker.record_route(
        opportunity(
            "VANRY:bingx:binance",
            "bingx",
            "binance",
        ),
        coverage={
            "coverage": "unsupported",
            "unsupported_exchanges": [
                "bingx",
                "binance",
            ],
        },
    )

    stats = tracker.exchange_statistics(
        "bingx"
    )

    assert stats[
        "route_mentions"
    ] == 1

    assert stats[
        "unsupported_mentions"
    ] == 1


def test_counts_repeated_exchange_demand():
    tracker = ExternalVenueCoverageDemandTracker()

    for index in range(3):
        tracker.record_route(
            opportunity(
                f"COIN{index}:bingx:kucoin",
                "bingx",
                "kucoin",
            ),
            coverage={
                "coverage": "unsupported",
                "unsupported_exchanges": [
                    "bingx",
                ],
            },
        )

    stats = tracker.exchange_statistics(
        "bingx"
    )

    assert stats[
        "route_mentions"
    ] == 3

    assert stats[
        "unsupported_mentions"
    ] == 3


def test_partial_coverage_is_counted_separately():
    tracker = ExternalVenueCoverageDemandTracker()

    tracker.record_route(
        opportunity(
            "FLOW:binance:kucoin",
            "binance",
            "kucoin",
        ),
        coverage={
            "coverage": "partial",
            "unsupported_exchanges": [],
        },
    )

    stats = tracker.exchange_statistics(
        "binance"
    )

    assert stats[
        "partial_mentions"
    ] == 1

    assert stats[
        "unsupported_mentions"
    ] == 0


def test_source_attribution_is_preserved():
    tracker = ExternalVenueCoverageDemandTracker()

    tracker.record_route(
        opportunity(
            "VANRY:bingx:kucoin",
            "bingx",
            "kucoin",
            sources=[
                "finder",
                "coinmarketgap",
            ],
        ),
        coverage={
            "coverage": "unsupported",
            "unsupported_exchanges": [
                "bingx",
            ],
        },
    )

    stats = tracker.exchange_statistics(
        "bingx"
    )

    assert stats[
        "sources"
    ] == [
        "finder",
        "coinmarketgap",
    ]


def test_priority_ranking_prefers_highest_unsupported_demand():
    tracker = ExternalVenueCoverageDemandTracker()

    for _ in range(5):
        tracker.record_route(
            opportunity(
                "VANRY:bingx:kucoin",
                "bingx",
                "kucoin",
            ),
            coverage={
                "coverage": "unsupported",
                "unsupported_exchanges": [
                    "bingx",
                ],
            },
        )

    for _ in range(2):
        tracker.record_route(
            opportunity(
                "FLOW:kraken:kucoin",
                "kraken",
                "kucoin",
            ),
            coverage={
                "coverage": "unsupported",
                "unsupported_exchanges": [
                    "kraken",
                ],
            },
        )

    ranking = tracker.priority_ranking()

    assert ranking[0][
        "exchange"
    ] == "bingx"

    assert ranking[0][
        "unsupported_mentions"
    ] == 5

    assert ranking[1][
        "exchange"
    ] == "kraken"


def test_both_route_venues_receive_route_mentions():
    tracker = ExternalVenueCoverageDemandTracker()

    tracker.record_route(
        opportunity(
            "FLOW:htx:okx",
            "htx",
            "okx",
        ),
        coverage={
            "coverage": "full",
            "unsupported_exchanges": [],
        },
    )

    assert tracker.exchange_statistics(
        "htx"
    )[
        "route_mentions"
    ] == 1

    assert tracker.exchange_statistics(
        "okx"
    )[
        "route_mentions"
    ] == 1


def test_unknown_exchange_returns_zero_statistics():
    tracker = ExternalVenueCoverageDemandTracker()

    stats = tracker.exchange_statistics(
        "unknown"
    )

    assert stats[
        "route_mentions"
    ] == 0

    assert stats[
        "unsupported_mentions"
    ] == 0


def test_tracker_is_paper_safe():
    tracker = ExternalVenueCoverageDemandTracker()

    result = tracker.record_route(
        opportunity(
            "FLOW:htx:okx",
            "htx",
            "okx",
        ),
        coverage={
            "coverage": "full",
            "unsupported_exchanges": [],
        },
    )

    assert result[
        "paper_only"
    ] is True

    assert result[
        "live_order_submitted"
    ] is False
