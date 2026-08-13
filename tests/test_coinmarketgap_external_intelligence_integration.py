from core.coinmarketgap_arbitrage_adapter import (
    CoinMarketGapArbitrageAdapter,
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


def coti_row():
    return {
        "project_id": "coti",
        "internal_ticker": "COTI",
        "stable": "USDT",
        "buy_exchange": "kucoin",
        "sell_exchange": "digifinex",
        "qty": 358403.15,
        "ask_price": 0.00995,
        "bid_price": 0.01149,
        "avg_buy": 0.0101402111,
        "avg_sell": 0.0114241365,
        "cost": 3634.2836069,
        "revenue": 4094.4464971,
        "profit": 458.6703902,
        "profit_pct": 0.1262065485,
        "internal_coin_name": "COTI",
        "buy_url": (
            "https://www.kucoin.com/"
            "trade/COTI-USDT"
        ),
        "sell_url": (
            "https://www.digifinex.com/"
            "en-ww/trade/USDT/COTI"
        ),
        "exploitable": True,
    }


def test_coinmarketgap_signal_flows_through_external_intelligence():
    adapter = CoinMarketGapArbitrageAdapter()
    normalizer = ExternalArbitrageSignalNormalizer()
    intake = ExternalArbitrageSignalIntake()
    correlator = ExternalArbitrageSignalCorrelator()
    tracker = (
        ExternalArbitrageSourcePerformanceTracker()
    )

    adapted = adapter.adapt(
        coti_row(),
        observed_at=1000.0,
    )

    normalized = normalizer.normalize(
        source="coinmarketgap",
        signal=adapted,
    )

    intake_result = intake.submit(
        normalized
    )

    correlation = correlator.correlate(
        normalized
    )

    attribution = tracker.record_signal(
        opportunity_key=(
            correlation["opportunity_key"]
        ),
        source=normalized["source"],
        source_signal_id=(
            normalized["source_signal_id"]
        ),
    )

    assert intake_result["accepted"] is True

    assert normalized[
        "source"
    ] == "coinmarketgap"

    assert normalized[
        "coin"
    ] == "COTI"

    assert normalized[
        "buy_exchange"
    ] == "kucoin"

    assert normalized[
        "sell_exchange"
    ] == "digifinex"

    assert normalized[
        "reported_status"
    ] == "exploitable"

    assert normalized[
        "reported_spread_percent"
    ] > 12.6

    assert correlation[
        "opportunity_key"
    ] == "COTI:kucoin:digifinex"

    assert attribution[
        "first_source"
    ] == "coinmarketgap"

    assert attribution[
        "sources"
    ] == [
        "coinmarketgap",
    ]

    # Critical safety boundary:
    # CoinMarketGap says exploitable,
    # ArbOS™ still requires independent verification.
    assert normalized[
        "arbos_verified"
    ] is False

    assert normalized[
        "executable"
    ] is False

    assert normalized[
        "verification_required"
    ] is True

    assert intake_result[
        "arbos_verified"
    ] is False

    assert intake_result[
        "executable"
    ] is False


def test_repeated_identical_coinmarketgap_row_is_deduplicated():
    adapter = CoinMarketGapArbitrageAdapter()
    normalizer = ExternalArbitrageSignalNormalizer()
    intake = ExternalArbitrageSignalIntake()

    first = normalizer.normalize(
        source="coinmarketgap",
        signal=adapter.adapt(
            coti_row(),
            observed_at=1000.0,
        ),
    )

    second = normalizer.normalize(
        source="coinmarketgap",
        signal=adapter.adapt(
            coti_row(),
            observed_at=1060.0,
        ),
    )

    assert intake.submit(
        first
    )["accepted"] is True

    duplicate = intake.submit(
        second
    )

    assert duplicate[
        "accepted"
    ] is False

    assert duplicate[
        "reason"
    ] == "duplicate_external_signal"
