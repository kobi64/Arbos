from core.hundred_coin_public_paper_scan_command import (
    DEFAULT_EXCHANGES,
    build_parser,
    summary,
)


def test_defaults_are_controlled_100_coin_run():
    args = (
        build_parser()
        .parse_args([])
    )

    assert args.coins == 100
    assert args.discovery_limit == 250
    assert args.starting_usdt == 100.0
    assert (
        args.max_slippage_percent
        == 0.5
    )
    assert (
        args.minimum_exchange_coverage
        == 2
    )

    assert tuple(
        args.exchanges
    ) == DEFAULT_EXCHANGES


def test_default_exchanges_are_profile_backed():
    assert DEFAULT_EXCHANGES == (
        "kucoin",
        "gate",
        "bitget",
        "htx",
    )


def test_operator_can_override_values():
    args = (
        build_parser()
        .parse_args([
            "--coins",
            "50",
            "--discovery-limit",
            "150",
            "--starting-usdt",
            "250",
            "--max-slippage-percent",
            "0.75",
            "--minimum-exchange-coverage",
            "3",
            "--exchanges",
            "kucoin",
            "gate",
        ])
    )

    assert args.coins == 50
    assert args.discovery_limit == 150
    assert args.starting_usdt == 250.0
    assert (
        args.max_slippage_percent
        == 0.75
    )
    assert (
        args.minimum_exchange_coverage
        == 3
    )
    assert args.exchanges == [
        "kucoin",
        "gate",
    ]


def test_summary_preserves_safety_state():
    result = {
        "readiness": "PASS",
        "reason": None,
        "requested_coin_count": 100,
        "approved_coin_count": 100,
        "approved_coin_assets": [
            "BTC",
            "ETH",
        ],
        "discovery": {
            "kucoin": {
                "discovery_ready": True,
                "selected_count": 200,
                "eligible_count": 500,
            },
        },
        "capacity_readiness": {
            "ready": True,
            "total_required_symbol_count": 180,
            "total_overflow_symbol_count": 0,
        },
        "scanner_result": {
            "route_count": 12,
            "failure_count": 3,
            "best_route": {
                "coin_asset": "BTC",
            },
        },
        "paper_only": True,
        "live_order_submitted": False,
    }

    item = summary(result)

    assert item[
        "readiness"
    ] == "PASS"

    assert item[
        "approved_coin_count"
    ] == 100

    assert item[
        "capacity_ready"
    ] is True

    assert item[
        "overflow_symbols"
    ] == 0

    assert item[
        "route_count"
    ] == 12

    assert item[
        "paper_only"
    ] is True

    assert (
        item[
            "live_order_submitted"
        ]
        is False
    )


def test_summary_handles_blocked_result():
    item = summary({
        "readiness": "FAIL",
        "reason": (
            "insufficient_cross_exchange_coin_coverage"
        ),
        "discovery": {},
        "paper_only": True,
        "live_order_submitted": False,
    })

    assert item[
        "readiness"
    ] == "FAIL"

    assert item["route_count"] == 0

    assert (
        item["live_order_submitted"]
        is False
    )
