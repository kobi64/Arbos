from core.sharpe_spot_transfer_adapter import (
    SharpeSpotTransferAdapter,
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


def sharpe_row():
    return {
        "symbol": "COTI",
        "buyExchange": "KuCoin",
        "sellExchange": "Bitget",
        "network": "ERC20",
        "buyAsk": 0.0100,
        "sellBid": 0.0112,
        "netProfitUsd": 31.50,
        "netProfitPct": 10.5,
        "grossSpreadPct": 12.0,
        "withdrawalFee": 5.0,
        "buyWithdrawEnabled": True,
        "sellDepositEnabled": True,
    }


def test_sharpe_signal_flows_through_external_intelligence():
    adapter = SharpeSpotTransferAdapter()
    normalizer = ExternalArbitrageSignalNormalizer()
    intake = ExternalArbitrageSignalIntake()
    correlator = ExternalArbitrageSignalCorrelator()
    tracker = (
        ExternalArbitrageSourcePerformanceTracker()
    )

    adapted = adapter.adapt(
        sharpe_row(),
        observed_at=1000.0,
    )

    normalized = normalizer.normalize(
        source="sharpe",
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
    assert normalized["source"] == "sharpe"
    assert normalized["coin"] == "COTI"

    assert normalized[
        "buy_exchange"
    ] == "kucoin"

    assert normalized[
        "sell_exchange"
    ] == "bitget"

    assert correlation[
        "opportunity_key"
    ] == "COTI:kucoin:bitget"

    assert attribution[
        "first_source"
    ] == "sharpe"

    assert normalized[
        "arbos_verified"
    ] is False

    assert normalized[
        "executable"
    ] is False

    assert normalized[
        "verification_required"
    ] is True


def test_sharpe_and_coinmarketgap_can_correlate_same_route():
    correlator = ExternalArbitrageSignalCorrelator()

    sharpe = {
        "source": "sharpe",
        "source_signal_id": "SHARPE-1",
        "coin": "COTI",
        "buy_exchange": "kucoin",
        "sell_exchange": "bitget",
        "reported_spread_percent": 10.5,
        "reported_status": "reported_profitable",
    }

    coinmarketgap = {
        "source": "coinmarketgap",
        "source_signal_id": "CMG-1",
        "coin": "COTI",
        "buy_exchange": "kucoin",
        "sell_exchange": "bitget",
        "reported_spread_percent": 9.8,
        "reported_status": "exploitable",
    }

    correlator.correlate(
        sharpe
    )

    correlator.correlate(
        coinmarketgap
    )

    record = correlator.get(
        "COTI:kucoin:bitget"
    )

    assert record[
        "sources"
    ] == [
        "sharpe",
        "coinmarketgap",
    ]

    assert record[
        "source_count"
    ] == 2

    assert record[
        "signal_count"
    ] == 2
