import pytest

from core.external_intelligence_discovery_expander import (
    ExternalIntelligenceDiscoveryExpander,
)


def candidate():
    return {
        "opportunity_key": "COTI:kucoin:digifinex",
        "source": "coinmarketgap",
        "source_signal_id": "CMG-001",
        "coin": "COTI",
        "buy_exchange": "kucoin",
        "sell_exchange": "digifinex",
        "arbos_verified": False,
        "verification_required": True,
    }


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
            "exchange_coin_assets": exchange_coin_assets,
            "fee_rates": fee_rates,
            "starting_usdt_value": starting_usdt_value,
            "max_slippage_percent": max_slippage_percent,
        })

        return {
            "best_route": {
                "route_id": "USDT-COTI-BTC-USDT",
                "route_type": "internal_triangle",
                "source_exchange": "kucoin",
                "executable": True,
            },
            "ranked_routes": [
                {
                    "route_id": "USDT-COTI-BTC-USDT",
                    "route_type": "internal_triangle",
                    "source_exchange": "kucoin",
                    "executable": True,
                },
                {
                    "route_id": (
                        "DIRECT-kucoin-COTI-digifinex"
                    ),
                    "route_type": "cross_exchange",
                    "source_exchange": "kucoin",
                    "destination_exchange": "digifinex",
                    "executable": True,
                },
            ],
            "paper_only": True,
            "live_order_submitted": False,
        }


def test_external_lead_triggers_both_exchanges():
    scanner = FakeScanner()

    expander = ExternalIntelligenceDiscoveryExpander(
        scanner=scanner,
    )

    expander.expand(
        candidate(),
        fee_rates={
            "kucoin": 0.001,
            "digifinex": 0.001,
        },
        starting_usdt_value=300.0,
        max_slippage_percent=0.5,
    )

    call = scanner.calls[0]

    assert call[
        "exchange_coin_assets"
    ] == {
        "kucoin": {"COTI"},
        "digifinex": {"COTI"},
    }


def test_external_lead_runs_unified_discovery():
    scanner = FakeScanner()

    result = ExternalIntelligenceDiscoveryExpander(
        scanner=scanner,
    ).expand(
        candidate(),
        fee_rates={
            "kucoin": 0.001,
            "digifinex": 0.001,
        },
        starting_usdt_value=300.0,
        max_slippage_percent=0.5,
    )

    assert result[
        "discovery_complete"
    ] is True

    assert len(
        result["ranked_routes"]
    ) == 2

    route_types = {
        route["route_type"]
        for route in result["ranked_routes"]
    }

    assert "internal_triangle" in route_types
    assert "cross_exchange" in route_types


def test_discovered_routes_preserve_trigger_attribution():
    result = ExternalIntelligenceDiscoveryExpander(
        scanner=FakeScanner(),
    ).expand(
        candidate(),
        fee_rates={
            "kucoin": 0.001,
            "digifinex": 0.001,
        },
        starting_usdt_value=300.0,
        max_slippage_percent=0.5,
    )

    for route in result[
        "ranked_routes"
    ]:
        assert route[
            "trigger_source"
        ] == "coinmarketgap"

        assert route[
            "trigger_signal_id"
        ] == "CMG-001"

        assert route[
            "trigger_opportunity_key"
        ] == (
            "COTI:kucoin:digifinex"
        )

        assert route[
            "discovery_source"
        ] == "arbos_native"


def test_exact_external_route_and_native_discovery_are_distinguishable():
    result = ExternalIntelligenceDiscoveryExpander(
        scanner=FakeScanner(),
    ).expand(
        candidate(),
        fee_rates={
            "kucoin": 0.001,
            "digifinex": 0.001,
        },
        starting_usdt_value=300.0,
        max_slippage_percent=0.5,
    )

    triangle = result[
        "ranked_routes"
    ][0]

    cross_exchange = result[
        "ranked_routes"
    ][1]

    assert triangle[
        "discovery_source"
    ] == "arbos_native"

    assert cross_exchange[
        "discovery_source"
    ] == "arbos_native"

    assert triangle[
        "trigger_source"
    ] == "coinmarketgap"

    assert cross_exchange[
        "trigger_source"
    ] == "coinmarketgap"


def test_fee_rates_are_passed_to_unified_scanner():
    scanner = FakeScanner()

    ExternalIntelligenceDiscoveryExpander(
        scanner=scanner,
    ).expand(
        candidate(),
        fee_rates={
            "kucoin": 0.001,
            "digifinex": 0.002,
        },
        starting_usdt_value=300.0,
        max_slippage_percent=0.5,
    )

    assert scanner.calls[0][
        "fee_rates"
    ] == {
        "kucoin": 0.001,
        "digifinex": 0.002,
    }


def test_candidate_coin_is_required():
    expander = ExternalIntelligenceDiscoveryExpander(
        scanner=FakeScanner(),
    )

    bad = candidate()
    bad["coin"] = ""

    with pytest.raises(
        ValueError,
        match="coin is required",
    ):
        expander.expand(
            bad,
            fee_rates={
                "kucoin": 0.001,
                "digifinex": 0.001,
            },
            starting_usdt_value=300.0,
            max_slippage_percent=0.5,
        )


def test_two_distinct_exchanges_are_required():
    expander = ExternalIntelligenceDiscoveryExpander(
        scanner=FakeScanner(),
    )

    bad = candidate()
    bad["sell_exchange"] = "kucoin"

    with pytest.raises(
        ValueError,
        match="distinct exchanges are required",
    ):
        expander.expand(
            bad,
            fee_rates={
                "kucoin": 0.001,
            },
            starting_usdt_value=300.0,
            max_slippage_percent=0.5,
        )


def test_expansion_is_paper_safe():
    result = ExternalIntelligenceDiscoveryExpander(
        scanner=FakeScanner(),
    ).expand(
        candidate(),
        fee_rates={
            "kucoin": 0.001,
            "digifinex": 0.001,
        },
        starting_usdt_value=300.0,
        max_slippage_percent=0.5,
    )

    assert result["paper_only"] is True

    assert result[
        "live_order_submitted"
    ] is False


def test_external_lead_can_expand_across_enabled_exchanges():
    scanner = FakeScanner()

    expander = ExternalIntelligenceDiscoveryExpander(
        scanner=scanner,
    )

    expander.expand_across_exchanges(
        candidate(),
        exchange_ids=[
            "kucoin",
            "digifinex",
            "gate",
            "htx",
            "xt",
            "bitget",
        ],
        fee_rates={
            "kucoin": 0.001,
            "digifinex": 0.001,
            "gate": 0.001,
            "htx": 0.002,
            "xt": 0.002,
            "bitget": 0.001,
        },
        starting_usdt_value=300.0,
        max_slippage_percent=0.5,
    )

    call = scanner.calls[0]

    assert call[
        "exchange_coin_assets"
    ] == {
        "kucoin": {"COTI"},
        "digifinex": {"COTI"},
        "gate": {"COTI"},
        "htx": {"COTI"},
        "xt": {"COTI"},
        "bitget": {"COTI"},
    }


def test_exchange_ids_are_normalized_and_deduplicated():
    scanner = FakeScanner()

    ExternalIntelligenceDiscoveryExpander(
        scanner=scanner,
    ).expand_across_exchanges(
        candidate(),
        exchange_ids=[
            " KUCOIN ",
            "digifinex",
            "KUCOIN",
            "gate",
        ],
        fee_rates={
            "kucoin": 0.001,
            "digifinex": 0.001,
            "gate": 0.001,
        },
        starting_usdt_value=300.0,
        max_slippage_percent=0.5,
    )

    assert scanner.calls[0][
        "exchange_coin_assets"
    ] == {
        "kucoin": {"COTI"},
        "digifinex": {"COTI"},
        "gate": {"COTI"},
    }


def test_expansion_requires_at_least_two_enabled_exchanges():
    expander = ExternalIntelligenceDiscoveryExpander(
        scanner=FakeScanner(),
    )

    with pytest.raises(
        ValueError,
        match="at least two exchanges are required",
    ):
        expander.expand_across_exchanges(
            candidate(),
            exchange_ids=["kucoin"],
            fee_rates={
                "kucoin": 0.001,
            },
            starting_usdt_value=300.0,
            max_slippage_percent=0.5,
        )


def test_all_enabled_exchanges_require_fee_rates():
    expander = ExternalIntelligenceDiscoveryExpander(
        scanner=FakeScanner(),
    )

    with pytest.raises(
        ValueError,
        match="fee rate is required for gate",
    ):
        expander.expand_across_exchanges(
            candidate(),
            exchange_ids=[
                "kucoin",
                "digifinex",
                "gate",
            ],
            fee_rates={
                "kucoin": 0.001,
                "digifinex": 0.001,
            },
            starting_usdt_value=300.0,
            max_slippage_percent=0.5,
        )


def test_global_expansion_preserves_external_trigger_attribution():
    result = ExternalIntelligenceDiscoveryExpander(
        scanner=FakeScanner(),
    ).expand_across_exchanges(
        candidate(),
        exchange_ids=[
            "kucoin",
            "digifinex",
            "gate",
        ],
        fee_rates={
            "kucoin": 0.001,
            "digifinex": 0.001,
            "gate": 0.001,
        },
        starting_usdt_value=300.0,
        max_slippage_percent=0.5,
    )

    assert result[
        "trigger_source"
    ] == "coinmarketgap"

    assert result[
        "trigger_coin"
    ] == "COTI"

    assert result[
        "expanded_exchange_count"
    ] == 3

    for route in result[
        "ranked_routes"
    ]:
        assert route[
            "trigger_source"
        ] == "coinmarketgap"

        assert route[
            "discovery_source"
        ] == "arbos_native"


def test_global_expansion_remains_paper_safe():
    result = ExternalIntelligenceDiscoveryExpander(
        scanner=FakeScanner(),
    ).expand_across_exchanges(
        candidate(),
        exchange_ids=[
            "kucoin",
            "digifinex",
        ],
        fee_rates={
            "kucoin": 0.001,
            "digifinex": 0.001,
        },
        starting_usdt_value=300.0,
        max_slippage_percent=0.5,
    )

    assert result["paper_only"] is True
    assert result[
        "live_order_submitted"
    ] is False


class FakeMarketSupport:
    def __init__(self, supported):
        self.supported = {
            key.lower(): {
                coin.upper()
                for coin in coins
            }
            for key, coins in supported.items()
        }

    def supports(
        self,
        exchange_id,
        coin,
    ):
        return (
            coin.upper()
            in self.supported.get(
                exchange_id.lower(),
                set(),
            )
        )


def test_market_aware_expansion_skips_unsupported_exchanges():
    scanner = FakeScanner()

    expander = ExternalIntelligenceDiscoveryExpander(
        scanner=scanner,
        market_support=FakeMarketSupport({
            "kucoin": {"COTI"},
            "digifinex": {"COTI"},
            "gate": set(),
            "htx": {"COTI"},
        }),
    )

    result = expander.expand_across_exchanges(
        candidate(),
        exchange_ids=[
            "kucoin",
            "digifinex",
            "gate",
            "htx",
        ],
        fee_rates={
            "kucoin": 0.001,
            "digifinex": 0.001,
            "gate": 0.001,
            "htx": 0.001,
        },
        starting_usdt_value=300.0,
        max_slippage_percent=0.5,
    )

    assert scanner.calls[0][
        "exchange_coin_assets"
    ] == {
        "kucoin": {"COTI"},
        "digifinex": {"COTI"},
        "htx": {"COTI"},
    }

    assert result[
        "skipped_exchanges"
    ] == [
        "gate",
    ]

    assert result[
        "expanded_exchange_count"
    ] == 3


def test_market_aware_expansion_requires_two_supported_exchanges():
    expander = ExternalIntelligenceDiscoveryExpander(
        scanner=FakeScanner(),
        market_support=FakeMarketSupport({
            "kucoin": {"COTI"},
            "digifinex": set(),
            "gate": set(),
        }),
    )

    with pytest.raises(
        ValueError,
        match="at least two supported exchanges are required",
    ):
        expander.expand_across_exchanges(
            candidate(),
            exchange_ids=[
                "kucoin",
                "digifinex",
                "gate",
            ],
            fee_rates={
                "kucoin": 0.001,
                "digifinex": 0.001,
                "gate": 0.001,
            },
            starting_usdt_value=300.0,
            max_slippage_percent=0.5,
        )


def test_market_support_is_optional_for_backward_compatibility():
    scanner = FakeScanner()

    expander = ExternalIntelligenceDiscoveryExpander(
        scanner=scanner,
    )

    expander.expand_across_exchanges(
        candidate(),
        exchange_ids=[
            "kucoin",
            "digifinex",
        ],
        fee_rates={
            "kucoin": 0.001,
            "digifinex": 0.001,
        },
        starting_usdt_value=300.0,
        max_slippage_percent=0.5,
    )

    assert scanner.calls[0][
        "exchange_coin_assets"
    ] == {
        "kucoin": {"COTI"},
        "digifinex": {"COTI"},
    }
