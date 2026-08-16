"""
ArbOS™
EX-255
One-Command Broad Public Paper Scan

Command-line entry point for the production broad public
paper scan application.

Public market data / paper execution only.
No authentication.
No transfers.
No live orders.
"""

import argparse
import json

import ccxt

from core.broad_public_paper_scan_application import (
    BroadPublicPaperScanApplication,
)


DEFAULT_EXCHANGES = [
    "binance",
    "bitget",
    "gate",
    "htx",
    "kucoin",
]


def build_parser():
    parser = argparse.ArgumentParser(
        description=(
            "Run an ArbOS broad public paper "
            "arbitrage scan."
        )
    )

    parser.add_argument(
        "--exchanges",
        nargs="+",
        default=DEFAULT_EXCHANGES,
        help=(
            "Public CCXT exchange IDs to scan."
        ),
    )

    parser.add_argument(
        "--coin-limit",
        type=int,
        default=100,
        help=(
            "Maximum number of liquid coins "
            "selected per exchange."
        ),
    )

    parser.add_argument(
        "--starting-usdt",
        type=float,
        default=100.0,
        help=(
            "Paper starting USDT value."
        ),
    )

    parser.add_argument(
        "--max-slippage",
        type=float,
        default=0.5,
        help=(
            "Maximum allowed slippage percent."
        ),
    )

    parser.add_argument(
        "--fee-rate",
        type=float,
        default=0.001,
        help=(
            "Default paper taker fee rate "
            "for every exchange."
        ),
    )

    return parser


def run_from_args(args, ccxt_module=ccxt):
    exchange_ids = [
        str(exchange_id).strip().lower()
        for exchange_id in args.exchanges
        if str(exchange_id).strip()
    ]

    if len(exchange_ids) < 2:
        raise ValueError(
            "at least two exchanges are required"
        )

    if args.coin_limit <= 0:
        raise ValueError(
            "coin_limit must be positive"
        )

    if args.starting_usdt <= 0:
        raise ValueError(
            "starting_usdt must be positive"
        )

    if args.max_slippage < 0:
        raise ValueError(
            "max_slippage must not be negative"
        )

    if args.fee_rate < 0:
        raise ValueError(
            "fee_rate must not be negative"
        )

    fee_rates = {
        exchange_id: args.fee_rate
        for exchange_id in exchange_ids
    }

    application = BroadPublicPaperScanApplication(
        ccxt_module=ccxt_module
    )

    result = application.run(
        exchange_ids=exchange_ids,
        fee_rates=fee_rates,
        starting_usdt_value=(
            args.starting_usdt
        ),
        max_slippage_percent=(
            args.max_slippage
        ),
        coin_limit=args.coin_limit,
    )

    record = dict(result)

    record["paper_only"] = True
    record["live_order_submitted"] = False

    return record


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)

    result = run_from_args(args)

    print(
        json.dumps(
            result,
            indent=2,
            sort_keys=True,
            default=str,
        )
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
