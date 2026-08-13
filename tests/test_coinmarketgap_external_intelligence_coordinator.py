from core.coinmarketgap_external_intelligence_coordinator import (
    CoinMarketGapExternalIntelligenceCoordinator,
)


class FakeClient:
    def fetch(
        self,
        exploitable_only=False,
    ):
        assert exploitable_only is True

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
        self.calls = []

    def record_signal(
        self,
        opportunity_key,
        source,
        source_signal_id,
    ):
        self.calls.append({
            "opportunity_key": opportunity_key,
            "source": source,
            "source_signal_id": source_signal_id,
        })

        return {
            "recorded": True,
            "first_source": source,
        }


def test_coordinator_ingests_exploitable_coinmarketgap_signal():
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

    result = coordinator.run_once()

    assert result[
        "fetch_complete"
    ] is True

    assert result[
        "candidate_count"
    ] == 1

    candidate = result[
        "candidates"
    ][0]

    assert candidate[
        "opportunity_key"
    ] == "COTI:kucoin:digifinex"

    assert candidate[
        "source"
    ] == "coinmarketgap"

    assert candidate[
        "verification_required"
    ] is True

    assert candidate[
        "arbos_verified"
    ] is False

    assert candidate[
        "executable"
    ] is False

    assert tracker.calls[0][
        "source"
    ] == "coinmarketgap"


def test_duplicate_intake_result_is_not_returned_as_candidate():
    class DuplicateIntake:
        def submit(
            self,
            signal,
        ):
            return {
                "accepted": False,
                "reason": "duplicate_external_signal",
            }

    coordinator = (
        CoinMarketGapExternalIntelligenceCoordinator(
            client=FakeClient(),
            adapter=FakeAdapter(),
            normalizer=FakeNormalizer(),
            intake=DuplicateIntake(),
            correlator=FakeCorrelator(),
            tracker=FakeTracker(),
            clock=lambda: 1000.0,
        )
    )

    result = coordinator.run_once()

    assert result[
        "candidate_count"
    ] == 0

    assert result[
        "duplicate_count"
    ] == 1


def test_failed_fetch_returns_empty_result():
    class FailedClient:
        def fetch(
            self,
            exploitable_only=False,
        ):
            return {
                "fetch_complete": False,
                "results": [],
            }

    coordinator = (
        CoinMarketGapExternalIntelligenceCoordinator(
            client=FailedClient(),
            adapter=FakeAdapter(),
            normalizer=FakeNormalizer(),
            intake=FakeIntake(),
            correlator=FakeCorrelator(),
            tracker=FakeTracker(),
            clock=lambda: 1000.0,
        )
    )

    result = coordinator.run_once()

    assert result[
        "fetch_complete"
    ] is False

    assert result[
        "candidate_count"
    ] == 0


def test_coordinator_is_paper_safe():
    coordinator = (
        CoinMarketGapExternalIntelligenceCoordinator(
            client=FakeClient(),
            adapter=FakeAdapter(),
            normalizer=FakeNormalizer(),
            intake=FakeIntake(),
            correlator=FakeCorrelator(),
            tracker=FakeTracker(),
            clock=lambda: 1000.0,
        )
    )

    result = coordinator.run_once()

    assert result["paper_only"] is True
    assert result[
        "live_order_submitted"
    ] is False
