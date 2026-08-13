from core.coinmarketgap_external_intelligence_coordinator import (
    CoinMarketGapExternalIntelligenceCoordinator,
)
from core.external_arbitrage_verification_bridge import (
    ExternalArbitrageVerificationBridge,
)


class FakeClient:
    def fetch(
        self,
        exploitable_only=False,
    ):
        return {
            "fetch_complete": True,
            "results": [
                {
                    "internal_ticker": "COTI",
                    "stable": "USDT",
                    "buy_exchange": "kucoin",
                    "sell_exchange": "digifinex",
                    "ask_price": 0.00995,
                    "bid_price": 0.01149,
                    "avg_buy": 0.01014,
                    "avg_sell": 0.01142,
                    "qty": 1000.0,
                    "cost": 10.14,
                    "revenue": 11.42,
                    "profit": 1.28,
                    "profit_pct": 0.126,
                    "exploitable": True,
                },
            ],
        }


class FakeAdapter:
    def adapt(
        self,
        row,
        observed_at,
    ):
        return {
            "signal_id": "CMG-1",
            "coin": "COTI",
            "buy_exchange": "kucoin",
            "sell_exchange": "digifinex",
            "buy_price": 0.00995,
            "sell_price": 0.01149,
            "spread_percent": 12.6,
            "status": "exploitable",
            "observed_at": observed_at,
        }


class FakeNormalizer:
    def normalize(
        self,
        source,
        signal,
    ):
        return {
            "source": source,
            "source_signal_id": signal["signal_id"],
            "signal_key": f"{source}:{signal['signal_id']}",
            "coin": signal["coin"],
            "buy_exchange": signal["buy_exchange"],
            "sell_exchange": signal["sell_exchange"],
            "reported_status": signal["status"],
            "reported_spread_percent": signal["spread_percent"],
            "arbos_verified": False,
            "executable": False,
            "verification_required": True,
        }


class FakeIntake:
    def submit(
        self,
        signal,
    ):
        return {
            **signal,
            "accepted": True,
        }


class FakeCorrelator:
    def correlate(
        self,
        signal,
    ):
        return {
            "opportunity_key": (
                "COTI:kucoin:digifinex"
            ),
            "sources": [
                "coinmarketgap",
            ],
        }


class FakeTracker:
    def __init__(self):
        self.signals = []
        self.verifications = []

    def record_signal(
        self,
        opportunity_key,
        source,
        source_signal_id,
    ):
        self.signals.append({
            "opportunity_key": opportunity_key,
            "source": source,
            "source_signal_id": source_signal_id,
        })

        return {
            "recorded": True,
        }

    def record_verification(
        self,
        opportunity_key,
        verified,
        executable,
    ):
        self.verifications.append({
            "opportunity_key": opportunity_key,
            "verified": verified,
            "executable": executable,
        })

        return {
            "recorded": True,
        }


class FakeRunner:
    def run(
        self,
        source_exchange_id,
        destination_exchange_id,
        scan_kwargs=None,
        prepare_kwargs=None,
    ):
        return {
            "scan_complete": True,
            "best_cross_exchange": {
                "route_id": (
                    "DIRECT-kucoin-COTI-digifinex"
                ),
                "executable": True,
                "net_profit": 7.5,
                "net_profit_percent": 2.5,
            },
            "paper_only": True,
            "live_order_submitted": False,
        }


def test_coinmarketgap_candidate_can_be_verified_end_to_end():
    tracker = FakeTracker()

    coordinator = (
        CoinMarketGapExternalIntelligenceCoordinator(
            client=FakeClient(),
            adapter=FakeAdapter(),
            normalizer=FakeNormalizer(),
            intake=FakeIntake(),
            correlator=FakeCorrelator(),
            tracker=tracker,
            clock=lambda: 1000.0,
        )
    )

    ingestion = coordinator.run_once()

    candidate = ingestion[
        "candidates"
    ][0]

    bridge = ExternalArbitrageVerificationBridge(
        runner=FakeRunner(),
        tracker=tracker,
    )

    result = bridge.verify(
        candidate,
        starting_usdt_value=300.0,
        source_fee_rate=0.001,
        destination_fee_rate=0.001,
        max_slippage_percent=0.5,
        minimum_profit_percent=0.5,
    )

    assert result[
        "arbos_verified"
    ] is True

    assert result[
        "executable"
    ] is True

    assert result[
        "verified_net_profit_percent"
    ] == 2.5

    assert tracker.signals[0][
        "source"
    ] == "coinmarketgap"

    assert tracker.verifications[0] == {
        "opportunity_key": (
            "COTI:kucoin:digifinex"
        ),
        "verified": True,
        "executable": True,
    }
