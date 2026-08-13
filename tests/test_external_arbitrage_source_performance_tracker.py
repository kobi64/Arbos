import pytest

from core.external_arbitrage_source_performance_tracker import (
    ExternalArbitrageSourcePerformanceTracker,
)


def test_records_new_source_signal():
    tracker = ExternalArbitrageSourcePerformanceTracker()

    result = tracker.record_signal(
        opportunity_key="COTI:gate:kucoin",
        source="coinmarketgap",
        source_signal_id="CMG-001",
    )

    assert result["recorded"] is True
    assert result["opportunity_key"] == "COTI:gate:kucoin"
    assert result["first_source"] == "coinmarketgap"
    assert result["sources"] == [
        "coinmarketgap",
    ]


def test_multiple_sources_are_preserved_for_same_opportunity():
    tracker = ExternalArbitrageSourcePerformanceTracker()

    tracker.record_signal(
        opportunity_key="COTI:gate:kucoin",
        source="coinmarketgap",
        source_signal_id="CMG-001",
    )

    tracker.record_signal(
        opportunity_key="COTI:gate:kucoin",
        source="arbihunt",
        source_signal_id="AH-001",
    )

    result = tracker.get_opportunity(
        "COTI:gate:kucoin"
    )

    assert result["first_source"] == "coinmarketgap"

    assert result["sources"] == [
        "coinmarketgap",
        "arbihunt",
    ]


def test_duplicate_source_does_not_duplicate_contributor():
    tracker = ExternalArbitrageSourcePerformanceTracker()

    tracker.record_signal(
        opportunity_key="COTI:gate:kucoin",
        source="coinmarketgap",
        source_signal_id="CMG-001",
    )

    tracker.record_signal(
        opportunity_key="COTI:gate:kucoin",
        source="coinmarketgap",
        source_signal_id="CMG-002",
    )

    result = tracker.get_opportunity(
        "COTI:gate:kucoin"
    )

    assert result["sources"] == [
        "coinmarketgap",
    ]

    assert result["source_signal_count"] == 2


def test_records_arbos_verification_outcome():
    tracker = ExternalArbitrageSourcePerformanceTracker()

    tracker.record_signal(
        opportunity_key="COTI:gate:kucoin",
        source="coinmarketgap",
        source_signal_id="CMG-001",
    )

    result = tracker.record_verification(
        opportunity_key="COTI:gate:kucoin",
        verified=True,
        executable=True,
    )

    assert result["arbos_verified"] is True
    assert result["executable"] is True


def test_records_paper_result_and_profit():
    tracker = ExternalArbitrageSourcePerformanceTracker()

    tracker.record_signal(
        opportunity_key="COTI:gate:kucoin",
        source="coinmarketgap",
        source_signal_id="CMG-001",
    )

    result = tracker.record_result(
        opportunity_key="COTI:gate:kucoin",
        successful=True,
        realized_profit=24.50,
        mode="paper",
    )

    assert result["successful"] is True
    assert result["realized_profit"] == 24.50
    assert result["mode"] == "paper"


def test_source_statistics_attribute_success_to_contributors():
    tracker = ExternalArbitrageSourcePerformanceTracker()

    tracker.record_signal(
        opportunity_key="COTI:gate:kucoin",
        source="coinmarketgap",
        source_signal_id="CMG-001",
    )

    tracker.record_signal(
        opportunity_key="COTI:gate:kucoin",
        source="arbihunt",
        source_signal_id="AH-001",
    )

    tracker.record_verification(
        opportunity_key="COTI:gate:kucoin",
        verified=True,
        executable=True,
    )

    tracker.record_result(
        opportunity_key="COTI:gate:kucoin",
        successful=True,
        realized_profit=20.0,
        mode="paper",
    )

    coinmarketgap = tracker.source_statistics(
        "coinmarketgap"
    )

    arbihunt = tracker.source_statistics(
        "arbihunt"
    )

    assert coinmarketgap["signals"] == 1
    assert coinmarketgap["verified"] == 1
    assert coinmarketgap["successful"] == 1

    assert arbihunt["signals"] == 1
    assert arbihunt["verified"] == 1
    assert arbihunt["successful"] == 1


def test_first_source_statistics_are_tracked_separately():
    tracker = ExternalArbitrageSourcePerformanceTracker()

    tracker.record_signal(
        opportunity_key="COTI:gate:kucoin",
        source="coinmarketgap",
        source_signal_id="CMG-001",
    )

    tracker.record_signal(
        opportunity_key="COTI:gate:kucoin",
        source="arbihunt",
        source_signal_id="AH-001",
    )

    tracker.record_result(
        opportunity_key="COTI:gate:kucoin",
        successful=True,
        realized_profit=15.0,
        mode="paper",
    )

    assert tracker.source_statistics(
        "coinmarketgap"
    )["first_source_successes"] == 1

    assert tracker.source_statistics(
        "arbihunt"
    )["first_source_successes"] == 0


def test_api_cost_and_net_value_are_reported():
    tracker = ExternalArbitrageSourcePerformanceTracker()

    tracker.set_source_cost(
        source="coinmarketgap",
        monthly_cost=49.0,
    )

    tracker.record_signal(
        opportunity_key="COTI:gate:kucoin",
        source="coinmarketgap",
        source_signal_id="CMG-001",
    )

    tracker.record_result(
        opportunity_key="COTI:gate:kucoin",
        successful=True,
        realized_profit=120.0,
        mode="paper",
    )

    stats = tracker.source_statistics(
        "coinmarketgap"
    )

    assert stats["gross_attributed_profit"] == 120.0
    assert stats["monthly_api_cost"] == 49.0
    assert stats["net_value_after_api_cost"] == 71.0


def test_missing_opportunity_key_is_rejected():
    tracker = ExternalArbitrageSourcePerformanceTracker()

    with pytest.raises(
        ValueError,
        match="opportunity_key is required",
    ):
        tracker.record_signal(
            opportunity_key="",
            source="coinmarketgap",
            source_signal_id="CMG-001",
        )


def test_tracker_is_paper_safe():
    tracker = ExternalArbitrageSourcePerformanceTracker()

    result = tracker.record_signal(
        opportunity_key="COTI:gate:kucoin",
        source="coinmarketgap",
        source_signal_id="CMG-001",
    )

    assert result["paper_only"] is True
    assert result["live_order_submitted"] is False


def test_tracks_direct_and_triggered_success_separately():
    tracker = ExternalArbitrageSourcePerformanceTracker()

    tracker.record_signal(
        opportunity_key="COTI:kucoin:digifinex",
        source="coinmarketgap",
        source_signal_id="CMG-001",
    )

    tracker.record_result(
        opportunity_key="COTI:kucoin:digifinex",
        successful=True,
        realized_profit=20.0,
        mode="paper",
    )

    tracker.record_triggered_discovery(
        source="coinmarketgap",
        trigger_opportunity_key="COTI:kucoin:digifinex",
        discovered_opportunity_key=(
            "USDT-COTI-BTC-USDT:kucoin"
        ),
        successful=True,
        realized_profit=12.0,
        mode="paper",
    )

    stats = tracker.source_statistics(
        "coinmarketgap"
    )

    assert stats[
        "direct_successful"
    ] == 1

    assert stats[
        "direct_profit"
    ] == 20.0

    assert stats[
        "triggered_native_successful"
    ] == 1

    assert stats[
        "triggered_native_profit"
    ] == 12.0

    assert stats[
        "total_source_value"
    ] == 32.0


def test_triggered_discovery_preserves_native_discovery_identity():
    tracker = ExternalArbitrageSourcePerformanceTracker()

    result = tracker.record_triggered_discovery(
        source="coinmarketgap",
        trigger_opportunity_key="COTI:kucoin:digifinex",
        discovered_opportunity_key=(
            "USDT-COTI-BTC-USDT:kucoin"
        ),
        successful=True,
        realized_profit=12.0,
        mode="paper",
    )

    assert result[
        "trigger_source"
    ] == "coinmarketgap"

    assert result[
        "discovery_source"
    ] == "arbos_native"

    assert result[
        "direct_external_discovery"
    ] is False


def test_triggered_profit_is_not_counted_as_direct_external_profit():
    tracker = ExternalArbitrageSourcePerformanceTracker()

    tracker.record_triggered_discovery(
        source="coinmarketgap",
        trigger_opportunity_key="COTI:kucoin:digifinex",
        discovered_opportunity_key=(
            "USDT-COTI-BTC-USDT:kucoin"
        ),
        successful=True,
        realized_profit=15.0,
        mode="paper",
    )

    stats = tracker.source_statistics(
        "coinmarketgap"
    )

    assert stats[
        "direct_profit"
    ] == 0.0

    assert stats[
        "triggered_native_profit"
    ] == 15.0
