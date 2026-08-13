import pytest

from core.external_arbitrage_signal_correlator import (
    ExternalArbitrageSignalCorrelator,
)


def signal(
    source,
    source_signal_id,
    coin="COTI",
    buy_exchange="gate",
    sell_exchange="kucoin",
):
    return {
        "source": source,
        "source_signal_id": source_signal_id,
        "coin": coin,
        "buy_exchange": buy_exchange,
        "sell_exchange": sell_exchange,
        "reported_spread_percent": 5.0,
        "reported_status": "exploitable",
    }


def test_builds_stable_opportunity_key():
    correlator = ExternalArbitrageSignalCorrelator()

    result = correlator.correlate(
        signal(
            "coinmarketgap",
            "CMG-001",
        )
    )

    assert result[
        "opportunity_key"
    ] == "COTI:gate:kucoin"


def test_same_route_from_multiple_sources_is_correlated():
    correlator = ExternalArbitrageSignalCorrelator()

    first = correlator.correlate(
        signal(
            "coinmarketgap",
            "CMG-001",
        )
    )

    second = correlator.correlate(
        signal(
            "arbihunt",
            "AH-001",
        )
    )

    assert first[
        "opportunity_key"
    ] == second[
        "opportunity_key"
    ]

    record = correlator.get(
        "COTI:gate:kucoin"
    )

    assert record[
        "sources"
    ] == [
        "coinmarketgap",
        "arbihunt",
    ]

    assert record[
        "source_count"
    ] == 2


def test_first_source_is_preserved():
    correlator = ExternalArbitrageSignalCorrelator()

    correlator.correlate(
        signal(
            "coinmarketgap",
            "CMG-001",
        )
    )

    correlator.correlate(
        signal(
            "arbihunt",
            "AH-001",
        )
    )

    record = correlator.get(
        "COTI:gate:kucoin"
    )

    assert record[
        "first_source"
    ] == "coinmarketgap"


def test_reverse_route_is_different_opportunity():
    correlator = ExternalArbitrageSignalCorrelator()

    first = correlator.correlate(
        signal(
            "coinmarketgap",
            "CMG-001",
            buy_exchange="gate",
            sell_exchange="kucoin",
        )
    )

    reverse = correlator.correlate(
        signal(
            "arbihunt",
            "AH-001",
            buy_exchange="kucoin",
            sell_exchange="gate",
        )
    )

    assert first[
        "opportunity_key"
    ] != reverse[
        "opportunity_key"
    ]


def test_same_source_multiple_signals_do_not_inflate_source_count():
    correlator = ExternalArbitrageSignalCorrelator()

    correlator.correlate(
        signal(
            "coinmarketgap",
            "CMG-001",
        )
    )

    correlator.correlate(
        signal(
            "coinmarketgap",
            "CMG-002",
        )
    )

    record = correlator.get(
        "COTI:gate:kucoin"
    )

    assert record[
        "source_count"
    ] == 1

    assert record[
        "signal_count"
    ] == 2


def test_missing_required_route_field_is_rejected():
    correlator = ExternalArbitrageSignalCorrelator()

    bad = signal(
        "coinmarketgap",
        "CMG-001",
    )

    bad["coin"] = ""

    with pytest.raises(
        ValueError,
        match="coin is required",
    ):
        correlator.correlate(
            bad
        )


def test_correlator_is_paper_safe():
    correlator = ExternalArbitrageSignalCorrelator()

    result = correlator.correlate(
        signal(
            "coinmarketgap",
            "CMG-001",
        )
    )

    assert result[
        "paper_only"
    ] is True

    assert result[
        "live_order_submitted"
    ] is False
