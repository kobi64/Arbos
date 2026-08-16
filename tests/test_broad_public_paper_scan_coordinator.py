import pytest

from core.broad_public_paper_scan_coordinator import (
    BroadPublicPaperScanCoordinator,
)


class FakeExchange:
    def __init__(
        self,
        exchange_id,
        markets,
        tickers,
    ):
        self.id = exchange_id
        self._markets = markets
        self._tickers = tickers

    def load_markets(self):
        return self._markets

    def fetch_tickers(self):
        return self._tickers


class FakeBootstrap:
    def __init__(self, exchanges):
        self._exchanges = exchanges

    def create(self, exchange_id):
        return self._exchanges[
            exchange_id
        ]


class FakeScanner:
    def __init__(self):
        self.calls = []

    def scan(
        self,
        exchange_coin_assets,
        fee_rates,
        starting_usdt_value,
        max_slippage_percent,
    ):
        self.calls.append({
            "exchange_coin_assets": (
                exchange_coin_assets
            ),
            "fee_rates": dict(
                fee_rates
            ),
            "starting_usdt_value": (
                starting_usdt_value
            ),
            "max_slippage_percent": (
                max_slippage_percent
            ),
        })

        return {
            "best_route": None,
            "ranked_routes": [],
            "route_count": 0,
            "paper_only": True,
            "live_order_submitted": False,
        }


def market(base):
    return {
        "base": base,
        "quote": "USDT",
        "spot": True,
        "active": True,
        "info": {
            "baseCoin": base,
        },
    }


def test_discovers_top_liquid_coins_per_exchange_and_scans():
    exchanges = {
        "kucoin": FakeExchange(
            exchange_id="kucoin",
            markets={
                "ETH/USDT": market("ETH"),
                "SOL/USDT": market("SOL"),
                "XRP/USDT": market("XRP"),
            },
            tickers={
                "ETH/USDT": {
                    "quoteVolume": 500.0,
                },
                "SOL/USDT": {
                    "quoteVolume": 900.0,
                },
                "XRP/USDT": {
                    "quoteVolume": 700.0,
                },
            },
        ),
        "gate": FakeExchange(
            exchange_id="gate",
            markets={
                "ETH/USDT": market("ETH"),
                "SOL/USDT": market("SOL"),
                "DOGE/USDT": market("DOGE"),
            },
            tickers={
                "ETH/USDT": {
                    "quoteVolume": 600.0,
                },
                "SOL/USDT": {
                    "quoteVolume": 1000.0,
                },
                "DOGE/USDT": {
                    "quoteVolume": 800.0,
                },
            },
        ),
    }

    scanner = FakeScanner()

    coordinator = (
        BroadPublicPaperScanCoordinator(
            bootstrap=FakeBootstrap(
                exchanges
            ),
            scanner=scanner,
        )
    )

    result = coordinator.run(
        exchange_ids=[
            "kucoin",
            "gate",
        ],
        fee_rates={
            "kucoin": 0.001,
            "gate": 0.002,
        },
        coin_limit=2,
        starting_usdt_value=100.0,
        max_slippage_percent=0.5,
    )

    assert result[
        "exchange_coin_assets"
    ] == {
        "gate": {
            "SOL",
            "DOGE",
        },
        "kucoin": {
            "SOL",
            "XRP",
        },
    }

    assert result[
        "configured_exchange_count"
    ] == 2

    assert result[
        "discovered_exchange_count"
    ] == 2

    assert result[
        "failed_exchange_count"
    ] == 0

    assert result[
        "paper_only"
    ] is True

    assert result[
        "live_order_submitted"
    ] is False

    assert len(
        scanner.calls
    ) == 1


def test_one_discovery_failure_does_not_stop_other_venues():
    class FailedExchange:
        id = "broken"

        def load_markets(self):
            raise RuntimeError(
                "market load failed"
            )

    exchanges = {
        "kucoin": FakeExchange(
            exchange_id="kucoin",
            markets={
                "ETH/USDT": market("ETH"),
            },
            tickers={
                "ETH/USDT": {
                    "quoteVolume": 500.0,
                },
            },
        ),
        "gate": FakeExchange(
            exchange_id="gate",
            markets={
                "ETH/USDT": market("ETH"),
            },
            tickers={
                "ETH/USDT": {
                    "quoteVolume": 600.0,
                },
            },
        ),
        "broken": FailedExchange(),
    }

    scanner = FakeScanner()

    coordinator = (
        BroadPublicPaperScanCoordinator(
            bootstrap=FakeBootstrap(
                exchanges
            ),
            scanner=scanner,
        )
    )

    result = coordinator.run(
        exchange_ids=[
            "kucoin",
            "gate",
            "broken",
        ],
        fee_rates={
            "kucoin": 0.001,
            "gate": 0.002,
            "broken": 0.001,
        },
        coin_limit=100,
        starting_usdt_value=100.0,
        max_slippage_percent=0.5,
    )

    assert result[
        "discovered_exchange_count"
    ] == 2

    assert result[
        "failed_exchange_count"
    ] == 1

    assert result[
        "failures"
    ][0][
        "exchange_id"
    ] == "broken"

    assert "RuntimeError" in (
        result["failures"][0][
            "error"
        ]
    )


def test_missing_fee_rate_fails_closed():
    coordinator = (
        BroadPublicPaperScanCoordinator(
            bootstrap=FakeBootstrap(
                {}
            ),
            scanner=FakeScanner(),
        )
    )

    with pytest.raises(
        ValueError,
        match="fee rate is required",
    ):
        coordinator.run(
            exchange_ids=[
                "toobit",
                "gate",
            ],
            fee_rates={
                "gate": 0.002,
            },
            coin_limit=100,
            starting_usdt_value=100.0,
            max_slippage_percent=0.5,
        )


def test_coin_limit_must_be_positive():
    coordinator = (
        BroadPublicPaperScanCoordinator(
            bootstrap=FakeBootstrap(
                {}
            ),
            scanner=FakeScanner(),
        )
    )

    with pytest.raises(
        ValueError,
        match="coin_limit must be positive",
    ):
        coordinator.run(
            exchange_ids=[
                "kucoin",
                "gate",
            ],
            fee_rates={
                "kucoin": 0.001,
                "gate": 0.002,
            },
            coin_limit=0,
            starting_usdt_value=100.0,
            max_slippage_percent=0.5,
        )
