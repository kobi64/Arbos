from core.finder_external_intelligence_coordinator import (
    FinderExternalIntelligenceCoordinator,
)
from core.external_arbitrage_verification_bridge import (
    ExternalArbitrageVerificationBridge,
)


class FakeClient:
    def fetch(self):
        return {
            "fetch_complete": True,
            "source": "finder",
            "feed": "landing-ticker",
            "results": [{
                "token": "VANRY",
                "quote": "USDT",
                "buyEx": "Bingx",
                "sellEx": "Kucoin",
                "buyP": 0.00177,
                "sellP": 0.00213,
                "spread": 20.0,
                "profit": 864.0,
                "cls": "veryhigh",
            }],
        }


class FakeAdapter:
    def adapt(
        self,
        row,
        observed_at,
    ):
        return {
            "signal_id": "FINDER-1",
            "coin": "VANRY",
            "buy_exchange": "bingx",
            "sell_exchange": "kucoin",
            "buy_price": 0.00177,
            "sell_price": 0.00213,
            "spread_percent": 20.0,
            "status": "reported_high_spread",
            "observed_at": observed_at,
            "arbos_verified": False,
            "executable": False,
            "verification_required": True,
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
            "signal_key": (
                f"{source}:{signal['signal_id']}"
            ),
            "coin": signal["coin"],
            "buy_exchange": signal["buy_exchange"],
            "sell_exchange": signal["sell_exchange"],
            "reported_status": signal["status"],
            "reported_spread_percent": (
                signal["spread_percent"]
            ),
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
                "VANRY:bingx:kucoin"
            ),
            "sources": ["finder"],
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
        return {"recorded": True}

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
        return {"recorded": True}


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
                    "DIRECT-bingx-VANRY-kucoin"
                ),
                "executable": True,
                "net_profit": 5.4,
                "net_profit_percent": 1.8,
            },
            "paper_only": True,
            "live_order_submitted": False,
        }


def test_finder_candidate_uses_existing_arbos_verification():
    tracker = FakeTracker()

    coordinator = FinderExternalIntelligenceCoordinator(
        client=FakeClient(),
        adapter=FakeAdapter(),
        normalizer=FakeNormalizer(),
        intake=FakeIntake(),
        correlator=FakeCorrelator(),
        tracker=tracker,
        clock=lambda: 1000.0,
    )

    ingestion = coordinator.run_once()

    candidate = ingestion[
        "candidates"
    ][0]

    result = ExternalArbitrageVerificationBridge(
        runner=FakeRunner(),
        tracker=tracker,
    ).verify(
        candidate,
        starting_usdt_value=300.0,
        source_fee_rate=0.001,
        destination_fee_rate=0.001,
        max_slippage_percent=0.5,
        minimum_profit_percent=0.5,
    )

    assert result["source"] == "finder"
    assert result["arbos_verified"] is True
    assert result["executable"] is True

    assert result[
        "verified_net_profit_percent"
    ] == 1.8

    assert tracker.verifications[0] == {
        "opportunity_key": (
            "VANRY:bingx:kucoin"
        ),
        "verified": True,
        "executable": True,
    }
