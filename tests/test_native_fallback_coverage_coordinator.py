from exchanges.native_fallback_coverage_coordinator import (
    NativeFallbackCoverageCoordinator,
)


class FakeFallbackRegistry:
    def has(self, exchange_id):
        return exchange_id == "kucoin"


def test_builds_complete_coverage_audit():
    coordinator = NativeFallbackCoverageCoordinator(
        fallback_registry=FakeFallbackRegistry()
    )

    result = coordinator.audit(
        exchange_id="kucoin",
        ccxt_symbols=[
            "BTC/USDT",
            "ETH/USDT",
        ],
        native_result={
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
                    "order_types": [
                        "LIMIT",
                        "MARKET",
                    ],
                },
                {
                    "symbol": "ETH/USDT",
                    "status": "TRADING",
                    "order_types": [
                        "LIMIT",
                        "MARKET",
                    ],
                },
                {
                    "symbol": "COTI/USDT",
                    "status": "TRADING",
                    "order_types": [
                        "LIMIT",
                        "MARKET",
                    ],
                },
            ],
        },
    )

    assert result["exchange_id"] == "kucoin"
    assert result["ccxt_market_count"] == 2
    assert result["native_market_count"] == 3
    assert result["matched_count"] == 2
    assert result["raw_only_count"] == 1

    assert result["verified_raw_only_count"] == 1
    assert result["verified_raw_only"] == [
        "COTI/USDT",
    ]

    assert result["fallback_registered"] is True
    assert result["fallback_coverage"] == "AVAILABLE"


def test_non_trading_raw_only_is_not_verified():
    coordinator = NativeFallbackCoverageCoordinator(
        fallback_registry=FakeFallbackRegistry()
    )

    result = coordinator.audit(
        exchange_id="kucoin",
        ccxt_symbols=[],
        native_result={
            "fetch_complete": True,
            "symbols": [
                "OLD/USDT",
            ],
            "markets": [
                {
                    "symbol": "OLD/USDT",
                    "status": "SUSPENDED",
                    "order_types": [
                        "LIMIT",
                        "MARKET",
                    ],
                },
            ],
        },
    )

    assert result["raw_only_count"] == 1
    assert result["verified_raw_only_count"] == 0
    assert result["fallback_coverage"] == "NOT_REQUIRED"


def test_failed_native_fetch_is_fail_closed():
    coordinator = NativeFallbackCoverageCoordinator(
        fallback_registry=FakeFallbackRegistry()
    )

    result = coordinator.audit(
        exchange_id="kucoin",
        ccxt_symbols=[
            "BTC/USDT",
        ],
        native_result={
            "fetch_complete": False,
            "symbols": [],
            "markets": [],
        },
    )

    assert result["native_fetch_complete"] is False
    assert result["audit_complete"] is False
    assert result["fallback_coverage"] == "UNKNOWN"


def test_never_submits_live_order():
    coordinator = NativeFallbackCoverageCoordinator(
        fallback_registry=FakeFallbackRegistry()
    )

    result = coordinator.audit(
        exchange_id="kucoin",
        ccxt_symbols=[],
        native_result={
            "fetch_complete": True,
            "symbols": [],
            "markets": [],
        },
    )

    assert result["live_order_submitted"] is False
