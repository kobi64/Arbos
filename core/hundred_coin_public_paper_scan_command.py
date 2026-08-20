"""
ArbOS™

EX-352
100-Coin Public Paper Scan Operator Command

Public market data and paper execution only.
No authentication.
No transfers.
No live orders.
"""

import argparse
import json

import ccxt

from core.hundred_coin_public_paper_scan_application import (
    HundredCoinPublicPaperScanApplication,
)


DEFAULT_EXCHANGES = (
    "kucoin",
    "gate",
    "bitget",
    "htx",
)

DEFAULT_FEE_RATE = 0.001


def build_parser():
    parser = argparse.ArgumentParser(
        description=(
            "Run the ArbOS 100-coin "
            "public paper scan"
        )
    )

    parser.add_argument(
        "--coins",
        type=int,
        default=100,
    )

    parser.add_argument(
        "--discovery-limit",
        type=int,
        default=250,
    )

    parser.add_argument(
        "--starting-usdt",
        type=float,
        default=100.0,
    )

    parser.add_argument(
        "--max-slippage-percent",
        type=float,
        default=0.5,
    )

    parser.add_argument(
        "--minimum-exchange-coverage",
        type=int,
        default=2,
    )

    parser.add_argument(
        "--exchanges",
        nargs="+",
        default=list(
            DEFAULT_EXCHANGES
        ),
    )

    return parser


def run(args=None):
    parsed = build_parser().parse_args(
        args
    )

    exchange_ids = [
        str(exchange_id)
        .strip()
        .lower()
        for exchange_id in (
            parsed.exchanges
        )
        if str(exchange_id).strip()
    ]

    fee_rates = {
        exchange_id: (
            DEFAULT_FEE_RATE
        )
        for exchange_id in exchange_ids
    }

    application = (
        HundredCoinPublicPaperScanApplication(
            ccxt_module=ccxt
        )
    )

    result = application.run(
        exchange_ids=exchange_ids,
        fee_rates=fee_rates,
        starting_usdt_value=(
            parsed.starting_usdt
        ),
        max_slippage_percent=(
            parsed.max_slippage_percent
        ),
        requested_coin_count=(
            parsed.coins
        ),
        discovery_limit=(
            parsed.discovery_limit
        ),
        minimum_exchange_coverage=(
            parsed.minimum_exchange_coverage
        ),
    )

    return result


def summary(result):
    discovery = (
        result.get(
            "discovery",
            {},
        )
        or {}
    )

    scanner = (
        result.get(
            "scanner_result",
            {},
        )
        or {}
    )

    capacity = (
        result.get(
            "capacity_readiness",
            {},
        )
        or {}
    )

    return {
        "readiness": result.get(
            "readiness"
        ),
        "reason": result.get(
            "reason"
        ),
        "requested_coin_count": (
            result.get(
                "requested_coin_count"
            )
        ),
        "approved_coin_count": (
            result.get(
                "approved_coin_count"
            )
        ),
        "approved_coin_assets": (
            result.get(
                "approved_coin_assets",
                [],
            )
        ),
        "discovery": {
            exchange_id: {
                "ready": item.get(
                    "discovery_ready"
                ),
                "selected_count": (
                    item.get(
                        "selected_count",
                        0,
                    )
                ),
                "eligible_count": (
                    item.get(
                        "eligible_count",
                        0,
                    )
                ),
                "reason": item.get(
                    "reason"
                ),
            }
            for exchange_id, item in (
                discovery.items()
            )
        },
        "capacity_ready": (
            capacity.get("ready")
        ),
        "required_symbols": (
            capacity.get(
                "total_required_symbol_count"
            )
        ),
        "overflow_symbols": (
            capacity.get(
                "total_overflow_symbol_count"
            )
        ),
        "route_count": scanner.get(
            "route_count",
            0,
        ),
        "failure_count": scanner.get(
            "failure_count",
            0,
        ),
        "best_route": scanner.get(
            "best_route"
        ),
        "paper_only": result.get(
            "paper_only",
            False,
        ),
        "live_order_submitted": (
            result.get(
                "live_order_submitted",
                False,
            )
        ),
    }


def main():
    result = run()

    print(
        json.dumps(
            summary(result),
            indent=2,
            default=str,
        )
    )

    if result.get(
        "live_order_submitted",
        False,
    ):
        raise SystemExit(2)

    if result.get(
        "readiness"
    ) != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
