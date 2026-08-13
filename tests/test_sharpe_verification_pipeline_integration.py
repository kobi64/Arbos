from core.sharpe_external_intelligence_coordinator import (
    SharpeExternalIntelligenceCoordinator,
)
from core.external_arbitrage_verification_bridge import (
    ExternalArbitrageVerificationBridge,
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
            "results": [{
                "symbol": "COTI",
                "buyExchange": "KuCoin",
                "sellExchange": "Bitget",
                "buyAsk": 0.0100,
                "sellBid": 0.0112,
                "netProfitPct": 10.5,
            }],
        }


class FakeAdapter:
    def adapt(self, row, observed_at):
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
    def normalize(self, source, signal):
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
    def submit(self, signal):
        return {
            **signal,
            "accepted": True,
        }


class FakeCorrelator:
    def correlate(self, signal):
        return {
            "opportunity_key": "COTI:kucoin:bitget",
            "sources": ["sharpe"],
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
                    "DIRECT-kucoin-COTI-bitget"
                ),
                "executable": True,
                "net_profit": 6.0,
                "net_profit_percent": 2.0,
            },
            "paper_only": True,
            "live_order_submitted": False,
        }


def test_sharpe_candidate_uses_existing_arbos_verification():
    tracker = FakeTracker()

    coordinator = SharpeExternalIntelligenceCoordinator(
        client=FakeClient(),
        adapter=FakeAdapter(),
        normalizer=FakeNormalizer(),
        intake=FakeIntake(),
        correlator=FakeCorrelator(),
        tracker=tracker,
        clock=lambda: 1000.0,
    )

    ingestion = coordinator.run_once(
        notional_usd=300.0,
        limit=10,
    )

    candidate = ingestion["candidates"][0]

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

    assert result["source"] == "sharpe"
    assert result["arbos_verified"] is True
    assert result["executable"] is True
    assert result["verified_net_profit_percent"] == 2.0

    assert tracker.verifications[0] == {
        "opportunity_key": "COTI:kucoin:bitget",
        "verified": True,
        "executable": True,
    }
