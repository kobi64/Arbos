import pytest

from core.unified_multi_exchange_public_paper_scanner import (
    UnifiedMultiExchangePublicPaperScanner,
)


class FakeVerificationRunner:
    def __init__(self):
        self.calls = []

    def run(
        self,
        source_exchange_id,
        destination_exchange_id,
        prepare_kwargs,
    ):
        coin = prepare_kwargs["coin_asset"]

        self.calls.append({
            "source_exchange_id": source_exchange_id,
            "destination_exchange_id": destination_exchange_id,
            "coin_asset": coin,
        })

        profit = {
            ("kucoin", "gate", "ETH"): 0.40,
            ("kucoin", "gate", "SOL"): 1.20,
            ("gate", "kucoin", "ETH"): -0.25,
        }[
            (
                source_exchange_id,
                destination_exchange_id,
                coin,
            )
        ]

        return {
            "ranked_routes": [
                {
                    "route_id": (
                        f"{source_exchange_id}-"
                        f"{destination_exchange_id}-"
                        f"{coin}"
                    ),
                    "coin_asset": coin,
                    "source_exchange": (
                        source_exchange_id
                    ),
                    "destination_exchange": (
                        destination_exchange_id
                    ),
                    "route_type": (
                        "direct_cross_exchange"
                    ),
                    "executable": True,
                    "net_profit_percent": profit,
                    "paper_only": True,
                    "live_order_submitted": False,
                },
            ],
            "paper_only": True,
            "live_order_submitted": False,
        }


def fee_rates():
    return {
        "kucoin": 0.001,
        "gate": 0.002,
    }


def test_scans_every_ordered_exchange_pair_and_common_coin():
    runner = FakeVerificationRunner()

    scanner = (
        UnifiedMultiExchangePublicPaperScanner(
            verification_runner=runner,
        )
    )

    result = scanner.scan(
        exchange_coin_assets={
            "kucoin": {
                "ETH",
                "SOL",
                "XRP",
            },
            "gate": {
                "ETH",
                "SOL",
                "ADA",
            },
        },
        fee_rates=fee_rates(),
        starting_usdt_value=100.0,
        max_slippage_percent=0.5,
    )

    assert result[
        "ordered_exchange_pair_count"
    ] == 2

    assert result[
        "coin_pair_scans"
    ] == 4

    assert len(runner.calls) == 4

    assert {
        (
            call["source_exchange_id"],
            call["destination_exchange_id"],
            call["coin_asset"],
        )
        for call in runner.calls
    } == {
        ("kucoin", "gate", "ETH"),
        ("kucoin", "gate", "SOL"),
        ("gate", "kucoin", "ETH"),
        ("gate", "kucoin", "SOL"),
    }


def test_ranks_all_returned_routes_globally():
    class RankingRunner:
        def run(
            self,
            source_exchange_id,
            destination_exchange_id,
            prepare_kwargs,
        ):
            coin = prepare_kwargs[
                "coin_asset"
            ]

            profit = {
                "ETH": 0.2,
                "SOL": 1.1,
            }[coin]

            return {
                "ranked_routes": [
                    {
                        "route_id": (
                            f"ROUTE-{coin}"
                        ),
                        "coin_asset": coin,
                        "route_type": (
                            "direct_cross_exchange"
                        ),
                        "executable": True,
                        "net_profit_percent": (
                            profit
                        ),
                    },
                ],
                "paper_only": True,
                "live_order_submitted": False,
            }

    result = (
        UnifiedMultiExchangePublicPaperScanner(
            verification_runner=(
                RankingRunner()
            ),
        ).scan(
            exchange_coin_assets={
                "kucoin": {"ETH", "SOL"},
                "gate": {"ETH", "SOL"},
            },
            fee_rates=fee_rates(),
            starting_usdt_value=100.0,
            max_slippage_percent=0.5,
        )
    )

    assert result[
        "ranked_routes"
    ][0]["coin_asset"] == "SOL"

    assert result[
        "best_route"
    ]["net_profit_percent"] == 1.1


def test_preserves_multiple_routes_from_single_coin_scan():
    class MultiRouteRunner:
        def run(
            self,
            source_exchange_id,
            destination_exchange_id,
            prepare_kwargs,
        ):
            return {
                "ranked_routes": [
                    {
                        "route_id": "INTERNAL",
                        "route_type": (
                            "internal_triangle"
                        ),
                        "executable": True,
                        "net_profit_percent": 0.3,
                    },
                    {
                        "route_id": "CROSS",
                        "route_type": (
                            "direct_cross_exchange"
                        ),
                        "executable": True,
                        "net_profit_percent": 0.7,
                    },
                ],
                "paper_only": True,
                "live_order_submitted": False,
            }

    result = (
        UnifiedMultiExchangePublicPaperScanner(
            verification_runner=(
                MultiRouteRunner()
            ),
        ).scan(
            exchange_coin_assets={
                "kucoin": {"ETH"},
                "gate": {"ETH"},
            },
            fee_rates=fee_rates(),
            starting_usdt_value=100.0,
            max_slippage_percent=0.5,
        )
    )

    route_ids = {
        route["route_id"]
        for route in result[
            "ranked_routes"
        ]
    }

    assert {
        "INTERNAL",
        "CROSS",
    }.issubset(route_ids)


def test_one_coin_failure_does_not_stop_matrix():
    class PartiallyFailingRunner:
        def run(
            self,
            source_exchange_id,
            destination_exchange_id,
            prepare_kwargs,
        ):
            coin = prepare_kwargs[
                "coin_asset"
            ]

            if coin == "SOL":
                raise RuntimeError(
                    "temporary failure"
                )

            return {
                "ranked_routes": [
                    {
                        "route_id": (
                            f"ROUTE-{coin}"
                        ),
                        "coin_asset": coin,
                        "executable": True,
                        "net_profit_percent": 0.1,
                    },
                ],
                "paper_only": True,
                "live_order_submitted": False,
            }

    result = (
        UnifiedMultiExchangePublicPaperScanner(
            verification_runner=(
                PartiallyFailingRunner()
            ),
        ).scan(
            exchange_coin_assets={
                "kucoin": {"ETH", "SOL"},
                "gate": {"ETH", "SOL"},
            },
            fee_rates=fee_rates(),
            starting_usdt_value=100.0,
            max_slippage_percent=0.5,
        )
    )

    assert result[
        "failed_coin_scans"
    ] == 2

    assert result[
        "successful_coin_scans"
    ] == 2

    assert len(
        result["failures"]
    ) == 2


def test_requires_at_least_two_exchanges():
    scanner = (
        UnifiedMultiExchangePublicPaperScanner(
            verification_runner=(
                FakeVerificationRunner()
            ),
        )
    )

    with pytest.raises(
        ValueError,
        match=(
            "at least two exchanges "
            "are required"
        ),
    ):
        scanner.scan(
            exchange_coin_assets={
                "kucoin": {"ETH"},
            },
            fee_rates={
                "kucoin": 0.001,
            },
            starting_usdt_value=100.0,
            max_slippage_percent=0.5,
        )


def test_unified_scanner_is_paper_only():
    result = (
        UnifiedMultiExchangePublicPaperScanner(
            verification_runner=(
                FakeVerificationRunner()
            ),
        ).scan(
            exchange_coin_assets={
                "kucoin": {"ETH"},
                "gate": {"ETH"},
            },
            fee_rates=fee_rates(),
            starting_usdt_value=100.0,
            max_slippage_percent=0.5,
        )
    )

    assert result["paper_only"] is True
    assert (
        result["live_order_submitted"]
        is False
    )
