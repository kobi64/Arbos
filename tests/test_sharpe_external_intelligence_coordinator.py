from core.sharpe_external_intelligence_coordinator import (
    SharpeExternalIntelligenceCoordinator,
)


class FakeClient:
    def fetch(
        self,
        notional_usd=300.0,
        limit=10,
    ):
        return {
            "fetch_complete": True,
            "kind": "cex-spot-transfer",
            "results": [
                {
                    "symbol": "COTI",
                    "buyExchange": "KuCoin",
                    "sellExchange": "Bitget",
                    "buyAsk": 0.0100,
                    "sellBid": 0.0112,
                    "netProfitPct": 10.5,
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
            "signal_id": "SHARPE-1",
            "coin": "COTI",
            "buy_exchange": "kucoin",
            "sell_exchange": "bitget",
            "buy_price": 0.0100,
            "sell_price": 0.0112,
            "spread_percent": 10.5,
            "status": "reported_profitable",
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
                "COTI:kucoin:bitget"
            ),
            "sources": [
                "sharpe",
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


def test_coordinator_ingests_sharpe_spot_signal():
    tracker = FakeTracker()

    coordinator = (
        SharpeExternalIntelligenceCoordinator(
            client=FakeClient(),
            adapter=FakeAdapter(),
            normalizer=FakeNormalizer(),
            intake=FakeIntake(),
            correlator=FakeCorrelator(),
            tracker=tracker,
            clock=lambda: 1000.0,
        )
    )

    result = coordinator.run_once(
        notional_usd=300.0,
        limit=10,
    )

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
    ] == "COTI:kucoin:bitget"

    assert candidate[
        "source"
    ] == "sharpe"

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
    ] == "sharpe"


def test_duplicate_signal_is_not_returned():
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
        SharpeExternalIntelligenceCoordinator(
            client=FakeClient(),
            adapter=FakeAdapter(),
            normalizer=FakeNormalizer(),
            intake=DuplicateIntake(),
            correlator=FakeCorrelator(),
            tracker=FakeTracker(),
            clock=lambda: 1000.0,
        )
    )

    result = coordinator.run_once(
        notional_usd=300.0,
        limit=10,
    )

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
            notional_usd=300.0,
            limit=10,
        ):
            return {
                "fetch_complete": False,
                "results": [],
            }

    coordinator = (
        SharpeExternalIntelligenceCoordinator(
            client=FailedClient(),
            adapter=FakeAdapter(),
            normalizer=FakeNormalizer(),
            intake=FakeIntake(),
            correlator=FakeCorrelator(),
            tracker=FakeTracker(),
            clock=lambda: 1000.0,
        )
    )

    result = coordinator.run_once(
        notional_usd=300.0,
        limit=10,
    )

    assert result[
        "fetch_complete"
    ] is False

    assert result[
        "candidate_count"
    ] == 0


def test_non_spot_kind_is_rejected():
    class WrongKindClient:
        def fetch(
            self,
            notional_usd=300.0,
            limit=10,
        ):
            return {
                "fetch_complete": True,
                "kind": "perpetual-arbitrage",
                "results": [],
            }

    coordinator = (
        SharpeExternalIntelligenceCoordinator(
            client=WrongKindClient(),
            adapter=FakeAdapter(),
            normalizer=FakeNormalizer(),
            intake=FakeIntake(),
            correlator=FakeCorrelator(),
            tracker=FakeTracker(),
            clock=lambda: 1000.0,
        )
    )

    result = coordinator.run_once(
        notional_usd=300.0,
        limit=10,
    )

    assert result[
        "fetch_complete"
    ] is False

    assert result[
        "reason"
    ] == "non_spot_transfer_payload"


def test_coordinator_is_paper_safe():
    coordinator = (
        SharpeExternalIntelligenceCoordinator(
            client=FakeClient(),
            adapter=FakeAdapter(),
            normalizer=FakeNormalizer(),
            intake=FakeIntake(),
            correlator=FakeCorrelator(),
            tracker=FakeTracker(),
            clock=lambda: 1000.0,
        )
    )

    result = coordinator.run_once(
        notional_usd=300.0,
        limit=10,
    )

    assert result["paper_only"] is True

    assert result[
        "live_order_submitted"
    ] is False
