from exchanges.native_fallback_discovery_runner import (
    NativeFallbackDiscoveryRunner,
)


class FakeExchange:
    id = "kucoin"

    def load_markets(self):
        return {
            "BTC/USDT": {
                "spot": True,
                "active": True,
            },
            "ETH/USDT": {
                "spot": True,
                "active": True,
            },
        }


class FakeNativeSource:
    def fetch(self):
        return {
            "fetch_complete": True,
            "symbols": [
                "BTC/USDT",
                "ETH/USDT",
                "COTI/USDT",
            ],
            "markets": [
                {
                    "symbol": "BTC/USDT",
                    "status": "TRADING",
                    "order_types": ["LIMIT", "MARKET"],
                },
                {
                    "symbol": "ETH/USDT",
                    "status": "TRADING",
                    "order_types": ["LIMIT", "MARKET"],
                },
                {
                    "symbol": "COTI/USDT",
                    "status": "TRADING",
                    "order_types": ["LIMIT", "MARKET"],
                },
            ],
        }


class FakeFallbackRegistry:
    def has(self, exchange_id):
        return exchange_id == "kucoin"


def test_discovers_and_audits_exchange():
    runner = NativeFallbackDiscoveryRunner(
        fallback_registry=FakeFallbackRegistry()
    )

    result = runner.run(
        exchange=FakeExchange(),
        native_market_source=FakeNativeSource(),
    )

    assert result["exchange_id"] == "kucoin"
    assert result["ccxt_market_count"] == 2
    assert result["native_market_count"] == 3
    assert result["raw_only_count"] == 1
    assert result["verified_raw_only"] == [
        "COTI/USDT",
    ]
    assert result["fallback_coverage"] == "AVAILABLE"


def test_reports_discovered_ccxt_symbols():
    runner = NativeFallbackDiscoveryRunner(
        fallback_registry=FakeFallbackRegistry()
    )

    result = runner.run(
        exchange=FakeExchange(),
        native_market_source=FakeNativeSource(),
    )

    assert result["ccxt_symbols"] == [
        "BTC/USDT",
        "ETH/USDT",
    ]


def test_requires_exchange():
    runner = NativeFallbackDiscoveryRunner(
        fallback_registry=FakeFallbackRegistry()
    )

    try:
        runner.run(
            exchange=None,
            native_market_source=FakeNativeSource(),
        )
        assert False
    except ValueError as exc:
        assert str(exc) == "exchange is required"


def test_requires_native_market_source():
    runner = NativeFallbackDiscoveryRunner(
        fallback_registry=FakeFallbackRegistry()
    )

    try:
        runner.run(
            exchange=FakeExchange(),
            native_market_source=None,
        )
        assert False
    except ValueError as exc:
        assert str(exc) == (
            "native_market_source is required"
        )


def test_discovery_is_research_only():
    runner = NativeFallbackDiscoveryRunner(
        fallback_registry=FakeFallbackRegistry()
    )

    result = runner.run(
        exchange=FakeExchange(),
        native_market_source=FakeNativeSource(),
    )

    assert result["audit_complete"] is True
    assert result["live_order_submitted"] is False


def test_discovers_all_spot_markets_and_reports_status():
    class MixedExchange:
        id = "kucoin"

        def load_markets(self):
            return {
                "BTC/USDT": {
                    "spot": True,
                    "active": True,
                },
                "OLD/USDT": {
                    "spot": True,
                    "active": False,
                },
                "BTC/USDT:USDT": {
                    "spot": False,
                    "swap": True,
                    "active": True,
                },
            }

    class NativeSource:
        def fetch(self):
            return {
                "fetch_complete": True,
                "symbols": [
                    "BTC/USDT",
                    "OLD/USDT",
                ],
                "markets": [
                    {
                        "symbol": "BTC/USDT",
                        "status": "TRADING",
                        "order_types": [
                            "LIMIT",
                            "MARKET",
                        ],
                    },
                    {
                        "symbol": "OLD/USDT",
                        "status": "TRADING",
                        "order_types": [
                            "LIMIT",
                            "MARKET",
                        ],
                    },
                ],
            }

    runner = NativeFallbackDiscoveryRunner(
        fallback_registry=FakeFallbackRegistry()
    )

    result = runner.run(
        exchange=MixedExchange(),
        native_market_source=NativeSource(),
    )

    assert result["ccxt_symbols"] == [
        "BTC/USDT",
        "OLD/USDT",
    ]

    assert result[
        "discovered_ccxt_market_count"
    ] == 2

    assert result[
        "discovered_ccxt_active_spot_count"
    ] == 1

    assert result[
        "discovered_ccxt_inactive_spot_count"
    ] == 1

    assert result["ccxt_market_count"] == 2
    assert result["native_market_count"] == 2
    assert result["matched_count"] == 2


def test_alias_matches_are_removed_from_discrepancies():
    class AliasExchange:
        id = "kucoin"

        def load_markets(self):
            return {
                "BSV/USDT": {
                    "id": "BCHSV-USDT",
                    "spot": True,
                    "active": True,
                },
                "BTC/USDT": {
                    "id": "BTC-USDT",
                    "spot": True,
                    "active": True,
                },
            }

    class AliasNativeSource:
        def fetch(self):
            return {
                "fetch_complete": True,
                "symbols": [
                    "BCHSV/USDT",
                    "BTC/USDT",
                ],
                "markets": [
                    {
                        "symbol": "BCHSV/USDT",
                        "status": "TRADING",
                        "order_types": [
                            "LIMIT",
                            "MARKET",
                        ],
                        "raw": {
                            "symbol": "BCHSV-USDT",
                        },
                    },
                    {
                        "symbol": "BTC/USDT",
                        "status": "TRADING",
                        "order_types": [
                            "LIMIT",
                            "MARKET",
                        ],
                        "raw": {
                            "symbol": "BTC-USDT",
                        },
                    },
                ],
            }

    runner = NativeFallbackDiscoveryRunner(
        fallback_registry=FakeFallbackRegistry()
    )

    result = runner.run(
        exchange=AliasExchange(),
        native_market_source=AliasNativeSource(),
    )

    assert result["alias_match_count"] == 1

    assert result["alias_matches"] == [
        {
            "ccxt_symbol": "BSV/USDT",
            "native_symbol": "BCHSV/USDT",
            "native_market_id": "BCHSV-USDT",
        },
    ]

    assert result["matched_count"] == 1
    assert result["ccxt_only_count"] == 0
    assert result["raw_only_count"] == 0


def test_preserves_pre_reconciliation_market_counts():
    class AliasExchange:
        id = "kucoin"

        def load_markets(self):
            return {
                "BSV/USDT": {
                    "id": "BCHSV-USDT",
                    "spot": True,
                    "active": True,
                },
                "BTC/USDT": {
                    "id": "BTC-USDT",
                    "spot": True,
                    "active": True,
                },
            }

    class AliasNativeSource:
        def fetch(self):
            return {
                "fetch_complete": True,
                "symbols": [
                    "BCHSV/USDT",
                    "BTC/USDT",
                ],
                "markets": [
                    {
                        "symbol": "BCHSV/USDT",
                        "status": "TRADING",
                        "order_types": [
                            "LIMIT",
                            "MARKET",
                        ],
                        "raw": {
                            "symbol": "BCHSV-USDT",
                        },
                    },
                    {
                        "symbol": "BTC/USDT",
                        "status": "TRADING",
                        "order_types": [
                            "LIMIT",
                            "MARKET",
                        ],
                        "raw": {
                            "symbol": "BTC-USDT",
                        },
                    },
                ],
            }

    result = NativeFallbackDiscoveryRunner(
        fallback_registry=FakeFallbackRegistry()
    ).run(
        exchange=AliasExchange(),
        native_market_source=AliasNativeSource(),
    )

    assert result[
        "discovered_ccxt_market_count"
    ] == 2

    assert result[
        "discovered_native_market_count"
    ] == 2

    assert result[
        "reconciled_ccxt_market_count"
    ] == 1

    assert result[
        "reconciled_native_market_count"
    ] == 1

    assert result["alias_match_count"] == 1
