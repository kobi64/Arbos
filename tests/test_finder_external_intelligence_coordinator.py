from core.finder_external_intelligence_coordinator import (
    FinderExternalIntelligenceCoordinator,
)


class FakeClient:
    def fetch(self):
        return {
            "fetch_complete": True,
            "source": "finder",
            "feed": "landing-ticker",
            "results": [
                {
                    "token": "VANRY",
                    "quote": "USDT",
                    "buyEx": "Bingx",
                    "sellEx": "Kucoin",
                    "buyP": 0.00177,
                    "sellP": 0.00213,
                    "spread": 20.0,
                    "profit": 864.0,
                    "cls": "veryhigh",
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


def make_coordinator(
    intake=None,
    client=None,
):
    return FinderExternalIntelligenceCoordinator(
        client=client or FakeClient(),
        adapter=FakeAdapter(),
        normalizer=FakeNormalizer(),
        intake=intake or FakeIntake(),
        correlator=FakeCorrelator(),
        tracker=FakeTracker(),
        clock=lambda: 1000.0,
    )


def test_coordinator_ingests_finder_signal():
    coordinator = make_coordinator()

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
        "source"
    ] == "finder"

    assert candidate[
        "opportunity_key"
    ] == "VANRY:bingx:kucoin"

    assert candidate[
        "verification_required"
    ] is True

    assert candidate[
        "arbos_verified"
    ] is False

    assert candidate[
        "executable"
    ] is False


def test_tracker_attributes_signal_to_finder():
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

    coordinator.run_once()

    assert tracker.calls == [{
        "opportunity_key": (
            "VANRY:bingx:kucoin"
        ),
        "source": "finder",
        "source_signal_id": "FINDER-1",
    }]


def test_duplicate_signal_is_not_returned():
    class DuplicateIntake:
        def submit(
            self,
            signal,
        ):
            return {
                "accepted": False,
                "reason": (
                    "duplicate_external_signal"
                ),
            }

    coordinator = make_coordinator(
        intake=DuplicateIntake(),
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
        def fetch(self):
            return {
                "fetch_complete": False,
                "reason": "request_failed",
                "results": [],
            }

    coordinator = make_coordinator(
        client=FailedClient(),
    )

    result = coordinator.run_once()

    assert result[
        "fetch_complete"
    ] is False

    assert result[
        "candidate_count"
    ] == 0

    assert result[
        "candidates"
    ] == []


def test_coordinator_is_paper_safe():
    coordinator = make_coordinator()

    result = coordinator.run_once()

    assert result[
        "paper_only"
    ] is True

    assert result[
        "live_order_submitted"
    ] is False
