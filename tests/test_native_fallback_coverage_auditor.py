from exchanges.native_fallback_coverage_auditor import (
    NativeFallbackCoverageAuditor,
)


class FakeFallbackRegistry:
    def __init__(self, supported):
        self._supported = set(supported)

    def has(self, exchange_id):
        return exchange_id in self._supported


def comparison():
    return {
        "exchange_id": "kucoin",
        "ccxt_market_count": 1000,
        "raw_market_count": 1002,
        "matched_count": 1000,
        "ccxt_only_count": 0,
        "raw_only_count": 2,
        "raw_only": [
            "AAA/USDT",
            "BBB/USDT",
        ],
    }


def verified_registry():
    return {
        "verified_markets": [
            {
                "symbol": "AAA/USDT",
                "source": "RAW_ONLY",
                "verified": True,
            },
            {
                "symbol": "BBB/USDT",
                "source": "RAW_ONLY",
                "verified": True,
            },
        ],
        "rejected_markets": [],
    }


def test_reports_market_counts():
    auditor = NativeFallbackCoverageAuditor(
        fallback_registry=(
            FakeFallbackRegistry({"kucoin"})
        )
    )

    result = auditor.audit(
        exchange_id="kucoin",
        comparison_result=comparison(),
        verified_registry=verified_registry(),
    )

    assert result["ccxt_market_count"] == 1000
    assert result["native_market_count"] == 1002
    assert result["raw_only_count"] == 2


def test_counts_verified_raw_only_markets():
    auditor = NativeFallbackCoverageAuditor(
        fallback_registry=(
            FakeFallbackRegistry({"kucoin"})
        )
    )

    result = auditor.audit(
        exchange_id="kucoin",
        comparison_result=comparison(),
        verified_registry=verified_registry(),
    )

    assert result["verified_raw_only_count"] == 2

    assert result["verified_raw_only"] == [
        "AAA/USDT",
        "BBB/USDT",
    ]


def test_reports_available_fallback():
    auditor = NativeFallbackCoverageAuditor(
        fallback_registry=(
            FakeFallbackRegistry({"kucoin"})
        )
    )

    result = auditor.audit(
        exchange_id="kucoin",
        comparison_result=comparison(),
        verified_registry=verified_registry(),
    )

    assert result["fallback_registered"] is True
    assert result["fallback_coverage"] == "AVAILABLE"


def test_reports_missing_fallback():
    auditor = NativeFallbackCoverageAuditor(
        fallback_registry=(
            FakeFallbackRegistry(set())
        )
    )

    result = auditor.audit(
        exchange_id="gate",
        comparison_result=comparison(),
        verified_registry=verified_registry(),
    )

    assert result["fallback_registered"] is False
    assert result["fallback_coverage"] == "NOT_IMPLEMENTED"


def test_no_verified_raw_only_needs_no_fallback():
    registry = {
        "verified_markets": [],
        "rejected_markets": [],
    }

    auditor = NativeFallbackCoverageAuditor(
        fallback_registry=(
            FakeFallbackRegistry(set())
        )
    )

    result = auditor.audit(
        exchange_id="gate",
        comparison_result=comparison(),
        verified_registry=registry,
    )

    assert result["verified_raw_only_count"] == 0
    assert result["fallback_coverage"] == "NOT_REQUIRED"


def test_audit_is_research_only():
    auditor = NativeFallbackCoverageAuditor(
        fallback_registry=(
            FakeFallbackRegistry({"kucoin"})
        )
    )

    result = auditor.audit(
        exchange_id="kucoin",
        comparison_result=comparison(),
        verified_registry=verified_registry(),
    )

    assert result["audit_complete"] is True
    assert result["live_order_submitted"] is False


def test_preserves_ccxt_only_market_visibility():
    data = comparison()
    data["ccxt_only_count"] = 2
    data["ccxt_only"] = [
        "OLD1/USDT",
        "OLD2/USDT",
    ]

    auditor = NativeFallbackCoverageAuditor(
        fallback_registry=(
            FakeFallbackRegistry({"kucoin"})
        )
    )

    result = auditor.audit(
        exchange_id="kucoin",
        comparison_result=data,
        verified_registry=verified_registry(),
    )

    assert result["ccxt_only_count"] == 2
    assert result["ccxt_only"] == [
        "OLD1/USDT",
        "OLD2/USDT",
    ]


def test_exposes_rejected_raw_only_reasons():
    registry = verified_registry()

    registry["rejected_markets"] = [
        {
            "symbol": "OLD/USDT",
            "source": "RAW_ONLY",
            "verified": False,
            "reason": "native_market_not_tradable",
            "native_status": "SUSPENDED",
            "order_types": [
                "LIMIT",
                "MARKET",
            ],
        },
        {
            "symbol": "CCXTONLY/USDT",
            "source": "CCXT_ONLY",
            "verified": False,
            "reason": "ccxt_only_requires_review",
        },
    ]

    auditor = NativeFallbackCoverageAuditor(
        fallback_registry=(
            FakeFallbackRegistry({"kucoin"})
        )
    )

    result = auditor.audit(
        exchange_id="kucoin",
        comparison_result=comparison(),
        verified_registry=registry,
    )

    assert result[
        "rejected_raw_only_count"
    ] == 1

    assert result["rejected_raw_only"] == [
        {
            "symbol": "OLD/USDT",
            "reason": (
                "native_market_not_tradable"
            ),
            "native_status": "SUSPENDED",
            "order_types": [
                "LIMIT",
                "MARKET",
            ],
        },
    ]
