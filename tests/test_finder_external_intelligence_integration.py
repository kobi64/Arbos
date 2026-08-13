from core.finder_spot_intelligence_adapter import (
    FinderSpotIntelligenceAdapter,
)
from core.external_arbitrage_signal_normalizer import (
    ExternalArbitrageSignalNormalizer,
)
from core.external_arbitrage_signal_intake import (
    ExternalArbitrageSignalIntake,
)
from core.external_arbitrage_signal_correlator import (
    ExternalArbitrageSignalCorrelator,
)
from core.external_arbitrage_source_performance_tracker import (
    ExternalArbitrageSourcePerformanceTracker,
)


def finder_row():
    return {
        "token": "VANRY",
        "quote": "USDT",
        "buyEx": "Bingx",
        "sellEx": "Kucoin",
        "buyP": 0.0017747311903163387,
        "sellP": 0.002135231055051244,
        "spread": 20.0725,
        "profit": 864.6834,
        "cls": "veryhigh",
    }


def test_finder_signal_flows_through_external_intelligence():
    adapter = FinderSpotIntelligenceAdapter()
    normalizer = ExternalArbitrageSignalNormalizer()
    intake = ExternalArbitrageSignalIntake()
    correlator = ExternalArbitrageSignalCorrelator()
    tracker = ExternalArbitrageSourcePerformanceTracker()

    adapted = adapter.adapt(
        finder_row(),
        observed_at=1000.0,
    )

    normalized = normalizer.normalize(
        source="finder",
        signal=adapted,
    )

    intake_result = intake.submit(
        normalized
    )

    correlation = correlator.correlate(
        normalized
    )

    attribution = tracker.record_signal(
        opportunity_key=correlation[
            "opportunity_key"
        ],
        source=normalized["source"],
        source_signal_id=normalized[
            "source_signal_id"
        ],
    )

    assert intake_result["accepted"] is True
    assert normalized["source"] == "finder"
    assert normalized["coin"] == "VANRY"

    assert normalized[
        "buy_exchange"
    ] == "bingx"

    assert normalized[
        "sell_exchange"
    ] == "kucoin"

    assert correlation[
        "opportunity_key"
    ] == "VANRY:bingx:kucoin"

    assert attribution[
        "first_source"
    ] == "finder"

    assert normalized[
        "arbos_verified"
    ] is False

    assert normalized[
        "executable"
    ] is False

    assert normalized[
        "verification_required"
    ] is True


def test_finder_and_other_source_can_correlate_same_route():
    correlator = ExternalArbitrageSignalCorrelator()

    finder = {
        "source": "finder",
        "source_signal_id": "FINDER-1",
        "coin": "VANRY",
        "buy_exchange": "bingx",
        "sell_exchange": "kucoin",
        "reported_spread_percent": 20.0725,
        "reported_status": "reported_high_spread",
    }

    other = {
        "source": "coinmarketgap",
        "source_signal_id": "CMG-1",
        "coin": "VANRY",
        "buy_exchange": "bingx",
        "sell_exchange": "kucoin",
        "reported_spread_percent": 19.8,
        "reported_status": "exploitable",
    }

    correlator.correlate(
        finder
    )

    correlator.correlate(
        other
    )

    record = correlator.get(
        "VANRY:bingx:kucoin"
    )

    assert record[
        "sources"
    ] == [
        "finder",
        "coinmarketgap",
    ]

    assert record[
        "source_count"
    ] == 2

    assert record[
        "signal_count"
    ] == 2
