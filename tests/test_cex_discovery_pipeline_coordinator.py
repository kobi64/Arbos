import pytest

from core.cex_discovery_pipeline_coordinator import (
    CEXDiscoveryPipelineCoordinator,
)


class FakeMarketLoader:
    def load(self):
        return {
            "markets": {
                "kraken": {"BTC/USDT": {"spot": True}},
                "kucoin": {"BTC/USDT": {"spot": True}},
            },
            "failures": {
                "broken": {
                    "reason": "market_load_failed",
                    "error": "RuntimeError: unavailable",
                },
            },
        }


class FakeAutoScanner:
    def __init__(self):
        self.calls = []

    def scan(
        self,
        exchange_markets,
        quote_asset,
        bridge_asset,
        starting_value,
        max_slippage_percent,
        fee_type="taker",
    ):
        self.calls.append({
            "exchange_markets": exchange_markets,
            "quote_asset": quote_asset,
            "bridge_asset": bridge_asset,
            "starting_value": starting_value,
            "max_slippage_percent": max_slippage_percent,
            "fee_type": fee_type,
        })

        return [
            {
                "exchange_id": "kucoin",
                "route_id": "R2",
                "filled": True,
                "net_profit_percent": 0.4,
            },
            {
                "exchange_id": "kraken",
                "route_id": "R1",
                "filled": True,
                "net_profit_percent": 0.1,
            },
        ]


def test_loads_markets_and_runs_auto_discovered_scan():
    auto_scanner = FakeAutoScanner()

    coordinator = CEXDiscoveryPipelineCoordinator(
        market_loader=FakeMarketLoader(),
        auto_scanner=auto_scanner,
    )

    result = coordinator.run(
        quote_asset="USDT",
        bridge_asset="BTC",
        starting_value=100.0,
        max_slippage_percent=0.5,
    )

    assert len(result["results"]) == 2
    assert result["results"][0]["exchange_id"] == "kucoin"

    call = auto_scanner.calls[0]

    assert set(call["exchange_markets"]) == {
        "kraken",
        "kucoin",
    }
    assert call["quote_asset"] == "USDT"
    assert call["bridge_asset"] == "BTC"


def test_market_load_failures_are_preserved():
    coordinator = CEXDiscoveryPipelineCoordinator(
        market_loader=FakeMarketLoader(),
        auto_scanner=FakeAutoScanner(),
    )

    result = coordinator.run(
        quote_asset="USDT",
        bridge_asset="BTC",
        starting_value=100.0,
        max_slippage_percent=0.5,
    )

    assert "broken" in result["market_load_failures"]
    assert (
        result["market_load_failures"]["broken"]["reason"]
        == "market_load_failed"
    )
